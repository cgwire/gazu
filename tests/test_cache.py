import datetime
import unittest
from unittest.mock import patch

import gazu.cache
import gazu.client


class Counted:
    """A function that returns a new list on each call and counts the calls."""

    def __init__(self):
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return [self.calls]


def cached(**kwargs):
    function = Counted()
    # wraps() needs a name, which a callable instance does not have.
    function.__name__ = "counted"
    return function, gazu.cache.cache(function, **kwargs)


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        gazu.cache.enable()

    def tearDown(self):
        gazu.cache.disable()

    def test_values_are_cached_by_arguments(self):
        function, wrapper = cached()
        self.assertEqual(wrapper("a"), wrapper("a"))
        self.assertEqual(function.calls, 1)
        wrapper("b")
        wrapper("a", key=1)
        self.assertEqual(function.calls, 3)

    def test_global_switch_bypasses_the_cache(self):
        function, wrapper = cached()
        gazu.cache.disable()
        wrapper()
        wrapper()
        self.assertEqual(function.calls, 2)
        gazu.cache.enable()
        wrapper()
        wrapper()
        self.assertEqual(function.calls, 3)

    def test_function_switch_bypasses_the_cache(self):
        function, wrapper = cached()
        wrapper.disable_cache()
        wrapper()
        wrapper()
        self.assertEqual(function.calls, 2)
        wrapper.enable_cache()
        wrapper()
        wrapper()
        self.assertEqual(function.calls, 3)

    def test_caller_cannot_change_a_cached_value(self):
        _, wrapper = cached()
        wrapper().append("changed")
        self.assertEqual(wrapper(), [1])

    def test_max_size_removes_the_oldest_entry(self):
        function, wrapper = cached(maxsize=2)
        wrapper("a")
        wrapper("b")
        wrapper("c")
        wrapper("c")
        self.assertEqual(function.calls, 3)
        wrapper("a")
        self.assertEqual(function.calls, 4)

    def test_set_cache_max_size(self):
        function, wrapper = cached()
        wrapper.set_cache_max_size(1)
        wrapper("a")
        wrapper("b")
        wrapper("a")
        self.assertEqual(function.calls, 3)

    def test_cache_infos(self):
        _, wrapper = cached()
        wrapper("a")
        wrapper("a")
        wrapper("a")
        wrapper("b")
        infos = wrapper.get_cache_infos()
        self.assertEqual(infos["misses"], 2)
        self.assertEqual(infos["hits"], 2)
        self.assertEqual(infos["current_size"], 2)

    def test_expired_value_is_computed_again(self):
        function, wrapper = cached()
        wrapper()
        with patch("gazu.cache.is_cache_expired", return_value=True):
            self.assertEqual(wrapper(), [2])
        self.assertEqual(wrapper.get_cache_infos()["expired_hits"], 1)

    def test_set_cache_expire(self):
        _, wrapper = cached()
        wrapper.set_cache_expire(7)
        self.assertEqual(wrapper.get_cache_infos()["expire"], 7)

    def test_clear_cache_and_clear_all(self):
        for clear in (
            lambda wrapper: wrapper.clear_cache(),
            lambda wrapper: gazu.cache.clear_all(),
        ):
            function, wrapper = cached()
            wrapper()
            clear(wrapper)
            wrapper()
            self.assertEqual(function.calls, 2)

    def test_positional_client_is_accepted_and_isolated_by_token(self):
        function, wrapper = cached()
        client_a = gazu.client.create_client("http://host/api")
        client_a.access_token = "token-a"
        client_b = gazu.client.create_client("http://host/api")
        client_b.access_token = "token-b"
        wrapper("a", client_a)
        wrapper("a", client_a)
        self.assertEqual(function.calls, 1)
        wrapper("a", client_b)
        self.assertEqual(function.calls, 2)


class CacheHelpersTestCase(unittest.TestCase):
    def test_get_cache_key(self):
        for args, kwargs, expected in (
            ((), {}, ""),
            (("a", "b"), {}, '["a", "b"]'),
            ((), {"a": 1}, '{"a": 1}'),
            (("a",), {"b": 1}, '[["a"], {"b": 1}]'),
        ):
            with self.subTest(args=args, kwargs=kwargs):
                self.assertEqual(
                    gazu.cache.get_cache_key(args, kwargs), expected
                )

    def test_get_cache_key_isolates_keyword_clients_by_token(self):
        client = gazu.client.create_client("http://host/api")
        client.access_token = "token-a"
        key_a = gazu.cache.get_cache_key((), {"client": client})
        self.assertEqual(
            key_a, gazu.cache.get_cache_key((), {"client": client})
        )
        client.access_token = "token-b"
        self.assertNotEqual(
            key_a, gazu.cache.get_cache_key((), {"client": client})
        )

    def test_remove_oldest_entry(self):
        def memo():
            return {
                f"key{day}": {
                    "date_accessed": datetime.datetime(2020, 1, day),
                    "value": day,
                }
                for day in (1, 2, 3)
            }

        entries = memo()
        self.assertEqual(gazu.cache.remove_oldest_entry(entries, 2), "key1")
        self.assertEqual(sorted(entries), ["key2", "key3"])
        for maxsize in (0, 3):
            entries = memo()
            self.assertIsNone(gazu.cache.remove_oldest_entry(entries, maxsize))
            self.assertEqual(len(entries), 3)

    def test_is_cache_enabled_needs_both_switches(self):
        for setting, state, expected in (
            (True, True, True),
            (True, False, False),
            (False, True, False),
        ):
            with self.subTest(setting=setting, state=state):
                with patch.dict(gazu.cache.cache_settings, enabled=setting):
                    self.assertEqual(
                        gazu.cache.is_cache_enabled({"enabled": state}),
                        expected,
                    )

    def test_is_cache_expired(self):
        now = datetime.datetime.now()
        for age, expire, expected in (
            (0, 3600, False),
            (7200, 3600, True),
            (7200, 0, False),
        ):
            with self.subTest(age=age, expire=expire):
                memo = {
                    "key": {
                        "date_accessed": now - datetime.timedelta(seconds=age)
                    }
                }
                self.assertEqual(
                    gazu.cache.is_cache_expired(
                        memo, {"expire": expire}, "key"
                    ),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
