"""
Unit tests for the AmshaJobConfig schema's memory/checkpoint crew fields.

These fields were added so the crew-level `memory`/`checkpoint` keys in
job_config.yaml survive validation + model_dump() and reach the file manager.
"""
import unittest

from amsha.configuration.domain.models.amsha_job_config import (
    AmshaJobConfig,
    CrewDefinition,
)


class TestCrewDefinition(unittest.TestCase):

    def _def(self, **kwargs) -> CrewDefinition:
        base = {"steps": [{"task_key": "t", "agent_key": "a"}]}
        base.update(kwargs)
        return CrewDefinition(**base)

    def test_defaults_off(self):
        crew_def = self._def()
        self.assertFalse(crew_def.memory)
        self.assertIsNone(crew_def.checkpoint)

    def test_memory_true_round_trips(self):
        crew_def = self._def(memory=True)
        self.assertIs(crew_def.memory, True)

    def test_checkpoint_dict_round_trips(self):
        crew_def = self._def(checkpoint={"enabled": True, "provider": "json", "location": "./ck"})
        self.assertEqual(crew_def.checkpoint["location"], "./ck")

    def test_checkpoint_bool_true_round_trips(self):
        crew_def = self._def(checkpoint=True)
        self.assertIs(crew_def.checkpoint, True)

    def test_full_job_config_keeps_crew_fields(self):
        job = AmshaJobConfig(
            crew_name="Copy Crew",
            usecase="copy",
            module_name="copy",
            output_filepath="output/crew.json",
            crews={
                "copy_crew": self._def(memory=True, checkpoint={"enabled": True, "location": "./ck"})
            },
            pipeline=["copy_crew"],
        )
        dumped = job.model_dump()
        dumped_crew = dumped["crews"]["copy_crew"]
        self.assertIs(dumped_crew["memory"], True)
        self.assertEqual(dumped_crew["checkpoint"]["location"], "./ck")


if __name__ == "__main__":
    unittest.main()