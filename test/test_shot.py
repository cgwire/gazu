import unittest
import json
import requests_mock

import gazu


class ShotTestCase(unittest.TestCase):

    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/shots'),
                text='[{"name": "Shot 01", "project_id": "project-1"}]'
            )
            shots = gazu.shot.all()
            shot_instance = shots[0]
            self.assertEquals(shot_instance["name"], "Shot 01")

    def test_all_with_filter(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/projects/project-1/shots'),
                text='[{"name": "Shot 01", "project_id": "project-1"}]'
            )
            project = {
                "id": "project-1"
            }
            shots = gazu.shot.all(project=project)
            self.assertEquals(len(shots), 1)
            shot_instance = shots[0]
            self.assertEquals(shot_instance["name"], "Shot 01")
            self.assertEquals(shot_instance["project_id"], "project-1")

    def test_all_for_sequence(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/sequences/sequence-1/shots'),
                text=json.dumps(
                    [
                        {
                            "name": "Shot 01",
                            "project_id": "project-1",
                            "parent_id": "sequence-1"
                        }
                    ]
                )
            )
            sequence = {
                "id": "sequence-1"
            }
            shots = gazu.shot.all_for_sequence(sequence=sequence)
            self.assertEquals(len(shots), 1)
            shot_instance = shots[0]
            self.assertEquals(shot_instance["name"], "Shot 01")
            self.assertEquals(shot_instance["project_id"], "project-1")
            self.assertEquals(shot_instance["parent_id"], "sequence-1")

    def test_all_sequences(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/sequences'),
                text='[{"name": "Sequence 01", "project_id": "project-1"}]'
            )
            sequences = gazu.shot.all_sequences()
            sequence_instance = sequences[0]
            self.assertEquals(sequence_instance["name"], "Sequence 01")

    def test_all_sequences_with_filter(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    'data/projects/project-1/sequences'
                ),
                text='[{"name": "Sequence 01", "project_id": "project-1"}]'
            )
            project = {
             "id": "project-1"
            }
            sequences = gazu.shot.all_sequences(project=project)
            self.assertEquals(len(sequences), 1)
            sequence_instance = sequences[0]
            self.assertEquals(sequence_instance["name"], "Sequence 01")
            self.assertEquals(sequence_instance["project_id"], "project-1")

    def test_all_episodes(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/episodes'),
                text='[{"name": "Episode 01", "project_id": "project-1"}]'
            )
            episodes = gazu.shot.all_episodes()
            episode_instance = episodes[0]
            self.assertEquals(episode_instance["name"], "Episode 01")

    def test_all_episodes_with_filter(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    'data/projects/project-1/episodes'
                ),
                text='[{"name": "Episode 01", "project_id": "project-1"}]'
            )
            project = {
                "id": "project-1"
            }
            episodes = gazu.shot.all_episodes(project=project)
            self.assertEquals(len(episodes), 1)
            episode_instance = episodes[0]
            self.assertEquals(episode_instance["name"], "Episode 01")
            self.assertEquals(episode_instance["project_id"], "project-1")

    def test_all_sequences_for_episode(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    'data/episodes/episode-1/sequences'),
                text=json.dumps(
                    [
                        {
                            "name": "Sequence 01",
                            "project_id": "project-1",
                            "parent_id": "episode-1"
                        }
                    ]
                )
            )
            episode = {
                "id": "episode-1"
            }
            sequences = gazu.shot.all_sequences_for_episode(episode)
            self.assertEquals(len(sequences), 1)
            sequence_instance = sequences[0]
            self.assertEquals(sequence_instance["name"], "Sequence 01")
            self.assertEquals(sequence_instance["project_id"], "project-1")
            self.assertEquals(sequence_instance["parent_id"], "episode-1")

    def test_task_types(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url('data/shots/shot-1/task_types'),
                text='[{"id": 1, "name": "Modeling"}]'
            )

            shot = {
                "id": "shot-1"
            }
            task_types = gazu.shot.task_types_for_shot(shot)
            task_type = task_types[0]
            self.assertEquals(task_type["name"], "Modeling")
