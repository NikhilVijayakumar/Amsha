import unittest
import time
import sys
from unittest.mock import MagicMock, patch
from nikhil.amsha.crew_forge.utils.token_monitor import TokenMonitor

class TestTokenMonitor(unittest.TestCase):
    def test_monitor_flow(self):
        # Mock pynvml module
        with patch.dict(sys.modules, {'pynvml': MagicMock()}):
            # Re-import or reload if needed, but since we patch sys.modules before TokenMonitor usage might be tricky if already imported.
            # Easier to patch the TokenMonitor's pynvml reference if it was imported at top level.
            # But TokenMonitor imports inside try/except block.
            
            # Let's patch where it is used in TokenMonitor if possible, or just mock the pynvml calls if it was successfully imported.
            # If pynvml is not installed in test env, TokenMonitor.GPU_AVAILABLE will be False.
            # We can force GPU_AVAILABLE to True for testing logic.
            
            monitor = TokenMonitor()
            
            # Force GPU availability for test
            with patch('nikhil.amsha.crew_forge.utils.token_monitor.GPU_AVAILABLE', True):
                with patch('nikhil.amsha.crew_forge.utils.token_monitor.pynvml') as mock_pynvml:
                    # Setup mocks
                    mock_pynvml.nvmlDeviceGetCount.return_value = 1
                    mock_handle = MagicMock()
                    mock_pynvml.nvmlDeviceGetHandleByIndex.return_value = mock_handle
                    
                    mock_mem = MagicMock()
                    mock_mem.used = 1024 * 1024 * 100 # 100 MB
                    mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem
                    
                    mock_util = MagicMock()
                    mock_util.gpu = 50
                    mock_pynvml.nvmlDeviceGetUtilizationRates.return_value = mock_util

                    # Test start monitoring
                    monitor.start_monitoring()
                    self.assertNotEqual(monitor.start_time, 0)
                    self.assertIn("gpu_0_start_mem", monitor.gpu_stats)
                    
                    # Simulate some work
                    time.sleep(0.1)
                    
                    # Change mock return for end
                    mock_mem.used = 1024 * 1024 * 200 # 200 MB
                    
                    # Test stop monitoring
                    monitor.stop_monitoring()
                    self.assertIn("gpu_0_end_mem", monitor.gpu_stats)
                    self.assertIn("gpu_0_utilization", monitor.gpu_stats)
                    
                    # Test log usage
                    mock_result = MagicMock()
                    mock_result.token_usage = {'total_tokens': 100, 'prompt_tokens': 40, 'completion_tokens': 60}
                    monitor.log_usage(mock_result)

                    # Test summary generation
                    summary = monitor.get_summary()
                    print(summary)
                    self.assertIn("Total Tokens: 100", summary)
                    self.assertIn("GPU Usage:", summary)
                    self.assertIn("GPU 0: Util 50%", summary)

if __name__ == '__main__':
    unittest.main()
