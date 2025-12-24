import unittest
from unittest.mock import patch
from datetime import datetime
from amsha.crew_forge.exceptions.crew_forge_exception import CrewForgeException
from amsha.crew_forge.exceptions.crew_execution_exception import CrewExecutionException
from amsha.crew_forge.exceptions.crew_manager_exception import CrewManagerException
from amsha.crew_forge.exceptions.crew_configuration_exception import CrewConfigurationException
from amsha.crew_forge.exceptions.input_preparation_exception import InputPreparationException
from amsha.crew_forge.exceptions.error_context import ErrorContext, ErrorMessageBuilder, wrap_external_exception

class TestCrewForgeExceptions(unittest.TestCase):
    def test_crew_forge_exception_str(self):
        # With details
        exc = CrewForgeException("Base error", "Some details")
        self.assertEqual(str(exc), "Base error: Some details")
        # Without details
        exc = CrewForgeException("Base error")
        self.assertEqual(str(exc), "Base error")

    def test_crew_execution_exception_str(self):
        # Full info
        exc = CrewExecutionException("Runtime error", "TestCrew", "Step 1")
        self.assertEqual(str(exc), "Crew 'TestCrew': Runtime error - Context: Step 1")
        # Only message
        exc = CrewExecutionException("Runtime error")
        self.assertEqual(str(exc), "Runtime error")
        # Message and crew
        exc = CrewExecutionException("Runtime error", crew_name="TestCrew")
        self.assertEqual(str(exc), "Crew 'TestCrew': Runtime error")
        # Message and context
        exc = CrewExecutionException("Runtime error", execution_context="Step 1")
        self.assertEqual(str(exc), "Runtime error - Context: Step 1")

    def test_crew_manager_exception_str(self):
        # Full info
        exc = CrewManagerException("Manager error", "FileManager", "File ops")
        self.assertEqual(str(exc), "FileManager: Manager error (Operation: File ops)")
        # Only message
        exc = CrewManagerException("Manager error")
        self.assertEqual(str(exc), "Manager error")

    def test_crew_configuration_exception_str(self):
        # Full info
        exc = CrewConfigurationException("Config error", "TestCrew", "Missing field 'agents'")
        self.assertEqual(str(exc), "Crew 'TestCrew': Config error - Missing field 'agents'")
        # Only message
        exc = CrewConfigurationException("Config error")
        self.assertEqual(str(exc), "Config error")

    def test_input_preparation_exception_str(self):
        # Full info
        exc = InputPreparationException("Prep error", "TestCrew", "config.yaml")
        self.assertEqual(str(exc), "Crew 'TestCrew': Prep error (Source: config.yaml)")
        # Only message
        exc = InputPreparationException("Prep error")
        self.assertEqual(str(exc), "Prep error")
        # Message and source
        exc = InputPreparationException("Prep error", input_source="config.yaml")
        self.assertEqual(str(exc), "Prep error (Source: config.yaml)")

    def test_error_context(self):
        ctx = ErrorContext("TestComponent", "TestOperation")
        self.assertEqual(ctx.component, "TestComponent")
        self.assertEqual(ctx.operation, "TestOperation")
        self.assertIsInstance(ctx.timestamp, datetime)
        
        # add_context
        ctx.add_context("key1", "val1").add_context("key2", 2)
        self.assertEqual(ctx.context_data, {"key1": "val1", "key2": 2})
        
        # create_message
        msg = ctx.create_message("Base error")
        self.assertEqual(msg, "[TestComponent] Base error during TestOperation")
        
        # create_message without operation
        ctx_no_op = ErrorContext("TestComponent")
        self.assertEqual(ctx_no_op.create_message("Base error"), "[TestComponent] Base error")
        
        # get_context_details
        details = ctx.get_context_details()
        self.assertIn("key1=val1", details)
        self.assertIn("key2=2", details)
        
        # get_context_details empty
        self.assertEqual(ctx_no_op.get_context_details(), "")
        
        # to_dict
        d = ctx.to_dict()
        self.assertEqual(d["component"], "TestComponent")
        self.assertEqual(d["operation"], "TestOperation")
        self.assertEqual(d["context"], {"key1": "val1", "key2": 2})

    def test_error_message_builder(self):
        builder = ErrorMessageBuilder()
        
        # configuration_error
        msg = builder.configuration_error("TestCrew", "Missing key", "config.yaml")
        self.assertEqual(msg, "Configuration error for crew 'TestCrew': Missing key (Config: config.yaml)")
        msg_no_path = builder.configuration_error("TestCrew", "Missing key")
        self.assertEqual(msg_no_path, "Configuration error for crew 'TestCrew': Missing key")
        
        # execution_error
        msg = builder.execution_error("TestCrew", "Stage 1", "Timeout")
        self.assertEqual(msg, "Execution failed for crew 'TestCrew' during Stage 1: Timeout")
        
        # manager_error
        msg = builder.manager_error("FileManager", "Write", "Disk full")
        self.assertEqual(msg, "FileManager failed during Write: Disk full")
        
        # input_preparation_error
        msg = builder.input_preparation_error("TestCrew", "source.json", "Invalid JSON")
        self.assertEqual(msg, "Input preparation failed for crew 'TestCrew' from source 'source.json': Invalid JSON")

    def test_wrap_external_exception(self):
        ext_err = ValueError("Original error")
        ctx = ErrorContext("TestComp", "TestOp")
        ctx.add_context("crew_name", "TestCrew")
        ctx.add_context("execution_context", "Step 1")
        
        # Wrap with CrewExecutionException (has crew_name and execution_context in __init__)
        wrapped = wrap_external_exception(ext_err, ctx, CrewExecutionException)
        self.assertIsInstance(wrapped, CrewExecutionException)
        self.assertEqual(wrapped.crew_name, "TestCrew")
        self.assertEqual(wrapped.execution_context, "Step 1")
        self.assertIn("[TestComp] Original error during TestOp", str(wrapped))
        
        # Wrap with CrewForgeException (basic init)
        ctx_no_crew = ErrorContext("TestComp")
        wrapped_base = wrap_external_exception(ext_err, ctx_no_crew, CrewForgeException)
        self.assertIsInstance(wrapped_base, CrewForgeException)
        self.assertIn("[TestComp] Original error", str(wrapped_base))
        
        # Test TypeError fallback (e.g. Exception which doesn't take keyword arguments)
        wrapped_exc = wrap_external_exception(ext_err, ctx_no_crew, Exception)
        self.assertIsInstance(wrapped_exc, Exception)
        self.assertIn("[TestComp] Original error", str(wrapped_exc))

    def test_wrap_external_exception_no_init(self):
        ext_err = ValueError("Original error")
        ctx = ErrorContext("TestComp")
        # Mock hasattr to return False for __init__ to hit line 206
        with patch('amsha.crew_forge.exceptions.error_context.hasattr', return_value=False):
            wrapped = wrap_external_exception(ext_err, ctx, Exception)
            self.assertIsInstance(wrapped, Exception)
            self.assertIn("[TestComp] Original error", str(wrapped))

if __name__ == '__main__':
    unittest.main()
