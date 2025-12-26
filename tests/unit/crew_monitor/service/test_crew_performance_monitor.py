import unittest
from unittest.mock import MagicMock, patch
import time
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor

class TestCrewPerformanceMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = CrewPerformanceMonitor(model_name="test-model")

    def test_initialization(self):
        self.assertEqual(self.monitor.model_name, "test-model")
        self.assertEqual(self.monitor.total_tokens, 0)
        self.assertEqual(self.monitor.gpu_stats, {})

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('time.time')
    def test_start_monitoring(self, mock_time, mock_mem, mock_cpu):
        mock_time.return_value = 1000.0
        mock_cpu.return_value = 10.0
        mock_mem.return_value.used = 1024 * 1024 * 100 # 100 MB
        
        with patch('amsha.crew_monitor.service.crew_performance_monitor.GPU_AVAILABLE', False):
            self.monitor.start_monitoring()
            
        self.assertEqual(self.monitor.start_time, 1000.0)
        self.assertEqual(self.monitor.start_cpu_percent, 10.0)
        self.assertEqual(self.monitor.start_memory_usage, 1024 * 1024 * 100)

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('time.time')
    def test_stop_monitoring(self, mock_time, mock_mem, mock_cpu):
        mock_time.return_value = 1100.0
        mock_cpu.return_value = 20.0
        mock_mem.return_value.used = 1024 * 1024 * 200 # 200 MB
        
        with patch('amsha.crew_monitor.service.crew_performance_monitor.GPU_AVAILABLE', False):
            self.monitor.stop_monitoring()
            
        self.assertEqual(self.monitor.end_time, 1100.0)
        self.assertEqual(self.monitor.end_cpu_percent, 20.0)
        self.assertEqual(self.monitor.end_memory_usage, 1024 * 1024 * 200)

    def test_log_usage_dict(self):
        mock_result = MagicMock()
        mock_result.token_usage = {
            'total_tokens': 100,
            'prompt_tokens': 60,
            'completion_tokens': 40
        }
        self.monitor.log_usage(mock_result)
        self.assertEqual(self.monitor.total_tokens, 100)
        self.assertEqual(self.monitor.prompt_tokens, 60)
        self.assertEqual(self.monitor.completion_tokens, 40)

    def test_log_usage_object(self):
        mock_result = MagicMock()
        mock_usage = MagicMock()
        mock_usage.total_tokens = 200
        mock_usage.prompt_tokens = 120
        mock_usage.completion_tokens = 80
        mock_result.token_usage = mock_usage
        
        self.monitor.log_usage(mock_result)
        self.assertEqual(self.monitor.total_tokens, 200)
        self.assertEqual(self.monitor.prompt_tokens, 120)
        self.assertEqual(self.monitor.completion_tokens, 80)

    def test_log_usage_no_attr(self):
        mock_result = object()
        with patch('builtins.print') as mock_print:
            self.monitor.log_usage(mock_result)
            mock_print.assert_called_with("[CrewPerformanceMonitor] Warning: 'token_usage' not found in result.")

    def test_get_metrics(self):
        self.monitor.start_time = 1000.0
        self.monitor.end_time = 1010.5
        self.monitor.start_memory_usage = 1024 * 1024 * 100
        self.monitor.end_memory_usage = 1024 * 1024 * 150
        self.monitor.end_cpu_percent = 15.0
        self.monitor.total_tokens = 500
        
        metrics = self.monitor.get_metrics()
        gen = metrics["general"]
        self.assertEqual(gen["duration_seconds"], 10.5)
        self.assertEqual(gen["memory_usage_change_mb"], 50.0)
        self.assertEqual(gen["total_tokens"], 500)
        self.assertEqual(gen["cpu_usage_end_percent"], 15.0)

    def test_get_summary(self):
        self.monitor.start_time = 1000.0
        self.monitor.end_time = 1010.0
        self.monitor.start_memory_usage = 1024 * 1024 * 100
        self.monitor.end_memory_usage = 1024 * 1024 * 110
        self.monitor.end_cpu_percent = 5.0
        self.monitor.total_tokens = 100
        
        summary = self.monitor.get_summary()
        self.assertIn("Total Tokens: 100", summary)
        self.assertIn("Time Taken: 10.00 seconds", summary)
        self.assertIn("Memory Usage Change: 10.0 MB", summary)

    @patch('amsha.crew_monitor.service.crew_performance_monitor.pynvml')
    def test_gpu_monitoring_start(self, mock_nvml):
        mock_nvml.nvmlDeviceGetCount.return_value = 1
        mock_handle = MagicMock()
        mock_nvml.nvmlDeviceGetHandleByIndex.return_value = mock_handle
        mock_mem = MagicMock()
        mock_mem.used = 1024 * 1024 * 500 # 500 MB
        mock_nvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem
        
        with patch('amsha.crew_monitor.service.crew_performance_monitor.GPU_AVAILABLE', True):
            self.monitor.start_monitoring()
            
        self.assertEqual(self.monitor.gpu_stats["gpu_0_start_mem"], 1024 * 1024 * 500)

    @patch('amsha.crew_monitor.service.crew_performance_monitor.pynvml')
    def test_gpu_monitoring_stop(self, mock_nvml):
        mock_nvml.nvmlDeviceGetCount.return_value = 1
        mock_handle = MagicMock()
        mock_nvml.nvmlDeviceGetHandleByIndex.return_value = mock_handle
        mock_mem = MagicMock()
        mock_mem.used = 1024 * 1024 * 600 # 600 MB
        mock_nvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem
        mock_util = MagicMock()
        mock_util.gpu = 45
        mock_nvml.nvmlDeviceGetUtilizationRates.return_value = mock_util
        
        self.monitor.gpu_stats["gpu_0_start_mem"] = 1024 * 1024 * 500
        
        with patch('amsha.crew_monitor.service.crew_performance_monitor.GPU_AVAILABLE', True):
            self.monitor.stop_monitoring()
            
        self.assertEqual(self.monitor.gpu_stats["gpu_0_end_mem"], 1024 * 1024 * 600)
        self.assertEqual(self.monitor.gpu_stats["gpu_0_utilization"], 45)

    @patch('amsha.crew_monitor.service.crew_performance_monitor.pynvml')
    def test_gpu_metrics_and_summary(self, mock_nvml):
        self.monitor.gpu_stats = {
            "gpu_0_start_mem": 1024 * 1024 * 100,
            "gpu_0_end_mem": 1024 * 1024 * 150,
            "gpu_0_utilization": 30
        }
        
        with patch('amsha.crew_monitor.service.crew_performance_monitor.GPU_AVAILABLE', True):
            metrics = self.monitor.get_metrics()
            summary = self.monitor.get_summary()
            
        self.assertEqual(metrics["gpu"]["gpu_0"]["utilization_percent"], 30)
        self.assertEqual(metrics["gpu"]["gpu_0"]["memory_change_mb"], 50.0)
        self.assertIn("GPU Usage:", summary)
        self.assertIn("GPU_0: Util 30%", summary)

    @patch('amsha.crew_monitor.service.crew_performance_monitor.pynvml')
    def test_gpu_monitoring_stop_failure(self, mock_nvml):
        mock_nvml.nvmlDeviceGetCount.side_effect = Exception("Stop Error")
        with patch('amsha.crew_monitor.service.crew_performance_monitor.GPU_AVAILABLE', True), \
             patch('builtins.print') as mock_print:
            self.monitor.stop_monitoring()
            mock_print.assert_called_with("[CrewPerformanceMonitor] GPU monitoring failed to stop: Stop Error")

if __name__ == '__main__':
    unittest.main()
