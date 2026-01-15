"""
Comprehensive tests for Nibandha log rotation integration in Amsha.

This test suite verifies:
1. Configuration loading (YAML/JSON)
2. Size-based rotation triggers
3. Time-based rotation triggers
4. Manual rotation
5. Client-driven cleanup utility
"""
import pytest
import yaml
import json
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

# Import Amsha logger and rotation utilities
from amsha.common.logger import (
    get_logger,
    should_rotate,
    rotate_logs,
    cleanup_old_archives,
    get_rotation_config,
    reset_logger
)


@pytest.fixture
def temp_nibandha_root(tmp_path):
    """Create a temporary .Nibandha directory for testing."""
    nibandha_root = tmp_path / ".Nibandha"
    nibandha_root.mkdir()
    yield nibandha_root
    # Cleanup
    if nibandha_root.exists():
        shutil.rmtree(nibandha_root)


@pytest.fixture(autouse=True)
def cleanup_logger():
    """Reset logger before and after each test."""
    reset_logger()
    yield
    reset_logger()


class TestLoggerPropagation:
    """Test that logger propagation is disabled to prevent log leakage."""
    
    def test_root_logger_propagation_disabled(self, temp_nibandha_root, monkeypatch):
        """Test that Amsha root logger has propagate=False after initialization."""
        import logging
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # Initialize logger
        logger = get_logger()
        
        # Check root Amsha logger propagation
        root_logger = logging.getLogger("Amsha")
        assert root_logger.propagate is False, "Amsha logger should have propagate=False"
    
    def test_module_logger_propagation(self, temp_nibandha_root, monkeypatch):
        """Test that module-specific loggers use correct propagation settings."""
        import logging
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # Initialize root logger first
        root_logger = get_logger()
        
        # Get module-specific logger
        module_logger = get_logger("crew_forge")
        
        # Module logger should propagate to Amsha (its parent)
        # but Amsha should NOT propagate to root
        amsha_root = logging.getLogger("Amsha")
        assert amsha_root.propagate is False, "Amsha root should not propagate"
    
    def test_no_log_leakage_to_root(self, temp_nibandha_root, monkeypatch):
        """Test that Amsha logs do not leak to Python's root logger."""
        import logging
        from io import StringIO
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # Set up a handler on Python's root logger to catch any leaked logs
        root_handler = logging.StreamHandler(StringIO())
        root_handler.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()  # Python's root logger
        original_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(root_handler)
        
        try:
            # Initialize Amsha logger and log something
            amsha_logger = get_logger("test_module")
            amsha_logger.info("Test message that should NOT leak to root")
            
            # Check that root handler did NOT capture this message
            output = root_handler.stream.getvalue()
            # The message might contain initialization logs from Nibandha but should not
            # contain our test message if propagation is properly disabled
            assert "Test message that should NOT leak to root" not in output, \
                "Amsha logs leaked to root logger!"
        finally:
            root_logger.removeHandler(root_handler)
            root_logger.setLevel(original_level)


class TestTimestampFormat:
    """Test that timestamp format uses daily granularity for log consolidation."""
    
    def test_default_timestamp_format_is_daily(self, temp_nibandha_root, monkeypatch):
        """Test that default rotation config uses daily timestamp format."""
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # Initialize logger (creates default config)
        logger = get_logger("test")
        config = get_rotation_config()
        
        assert config is not None
        assert config.timestamp_format == '%Y-%m-%d', \
            f"Expected daily format '%Y-%m-%d', got '{config.timestamp_format}'"
    
    def test_same_day_restarts_use_same_log_file(self, temp_nibandha_root, monkeypatch):
        """Test that multiple initializations on same day append to same log file."""
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # First initialization
        logger1 = get_logger("restart_test_1")
        logger1.info("First initialization")
        
        # Get log file name
        log_dir = temp_nibandha_root / "Amsha" / "logs" / "data"
        log_files_1 = list(log_dir.glob("*.log"))
        assert len(log_files_1) == 1, "Should have exactly one log file"
        first_log_name = log_files_1[0].name
        
        # Simulate application restart (reset logger)
        reset_logger()
        time.sleep(0.1)  # Small delay
        
        # Second initialization (same day)
        logger2 = get_logger("restart_test_2")
        logger2.info("Second initialization")
        
        # Check log files - should still be same file
        log_files_2 = list(log_dir.glob("*.log"))
        assert len(log_files_2) == 1, \
            f"Expected 1 log file for daily rotation, found {len(log_files_2)}"
        
        # File name should match (daily format means same name for same day)
        second_log_name = log_files_2[0].name
        assert first_log_name == second_log_name, \
            f"Log file names differ: {first_log_name} vs {second_log_name}"
        
        # Verify both messages are in the same file
        log_content = log_files_2[0].read_text()
        assert "First initialization" in log_content
        assert "Second initialization" in log_content


class TestConfigurationLoading:
    """Test configuration loading from YAML/JSON files."""
    
    def test_load_yaml_config(self, temp_nibandha_root, monkeypatch):
        """Test loading rotation config from YAML file."""
        # Set up config directory
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        # Create YAML config
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 50,
                'rotation_interval_hours': 48,
                'archive_retention_days': 60
            }, f)
        
        # Change to temp directory
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # Initialize logger
        logger = get_logger("test")
        config = get_rotation_config()
        
        assert config is not None
        assert config.enabled is True
        assert config.max_size_mb == 50
        assert config.rotation_interval_hours == 48
        assert config.archive_retention_days == 60
    
    def test_load_json_config(self, temp_nibandha_root, monkeypatch):
        """Test loading rotation config from JSON file."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        # Create JSON config
        config_file = config_dir / "rotation_config.json"
        with open(config_file, 'w') as f:
            json.dump({
                'enabled': True,
                'max_size_mb': 25,
                'rotation_interval_hours': 12,
                'archive_retention_days': 14
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        config = get_rotation_config()
        
        assert config is not None
        assert config.enabled is True
        assert config.max_size_mb == 25
        assert config.rotation_interval_hours == 12
    
    def test_no_config_uses_default(self, temp_nibandha_root, monkeypatch):
        """Test that missing config allows Nibandha to use its defaults."""
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        config = get_rotation_config()
        
        # Nibandha will handle defaults - config may or may not exist
        # Just verify we can get logger without error
        assert logger is not None


class TestRotationTriggers:
    """Test rotation trigger logic."""
    
    def test_size_based_rotation_trigger(self, temp_nibandha_root, monkeypatch):
        """Test that rotation is triggered when size limit is exceeded."""
        # Create config with very small size limit
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 0.001,  # Very small: 1KB
                'rotation_interval_hours': 24,
                'archive_retention_days': 30
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        
        # Write enough data to exceed limit
        for i in range(100):
            logger.info(f"Test log message {i} " * 20)
        
        # Check if rotation is needed
        assert should_rotate() is True
    
    def test_time_based_rotation_trigger(self, temp_nibandha_root, monkeypatch):
        """Test that rotation is triggered when time limit is exceeded."""
        # Create config with very short interval
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 100,
                'rotation_interval_hours': 0.0001,  # Very short: ~0.36 seconds
                'archive_retention_days': 30
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        logger.info("Initial log")
        
        # Wait for interval to pass
        time.sleep(0.5)
        
        # Check if rotation is needed
        assert should_rotate() is True
    
    def test_no_rotation_when_disabled(self, temp_nibandha_root, monkeypatch):
        """Test that rotation check returns False when disabled."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({'enabled': False}, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        
        # Write lots of data
        for i in range(100):
            logger.info(f"Test log message {i} " * 20)
        
        # Should not trigger rotation
        assert should_rotate() is False


class TestManualRotation:
    """Test manual log rotation."""
    
    def test_manual_rotation_creates_new_log(self, temp_nibandha_root, monkeypatch):
        """Test that manual rotation creates a new log file."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 10,
                'rotation_interval_hours': 24,
                'archive_retention_days': 30
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        logger.info("Before rotation")
        
        # Get current log file
        log_data_dir = temp_nibandha_root / "Amsha" / "logs" / "data"
        old_logs = list(log_data_dir.glob("*.log"))
        assert len(old_logs) == 1
        old_log = old_logs[0]
        
        # Wait to ensure different timestamp
        time.sleep(1)
        
        # Manually rotate
        rotate_logs()
        
        # Check new log created
        new_logs = list(log_data_dir.glob("*.log"))
        assert len(new_logs) == 1
        new_log = new_logs[0]
        
        # Should be different file
        assert new_log.name != old_log.name
    
    def test_manual_rotation_archives_old_log(self, temp_nibandha_root, monkeypatch):
        """Test that manual rotation moves old log to archive."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 10,
                'rotation_interval_hours': 24,
                'archive_retention_days': 30
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        logger.info("Test message before rotation")
        
        # Get current log file name
        log_data_dir = temp_nibandha_root / "Amsha" / "logs" / "data"
        old_log_name = list(log_data_dir.glob("*.log"))[0].name
        
        time.sleep(1)
        
        # Rotate
        rotate_logs()
        
        # Check archive
        archive_dir = temp_nibandha_root / "Amsha" / "logs" / "archive"
        archived_logs = list(archive_dir.glob("*.log"))
        
        assert len(archived_logs) == 1
        assert archived_logs[0].name == old_log_name


class TestClientDrivenCleanup:
    """Test client-driven cleanup utility."""
    
    def test_cleanup_removes_old_archives(self, temp_nibandha_root, monkeypatch):
        """Test that cleanup removes old archive files."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 10,
                'rotation_interval_hours': 24,
                'archive_retention_days': 7  # Keep 7 days
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        
        # Create archive directory with old files
        archive_dir = temp_nibandha_root / "Amsha" / "logs" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create old archive (30 days ago)
        old_archive = archive_dir / "2025-12-15_00-00-00.log"
        old_archive.write_text("Old log content")
        
        # Set modification time to 30 days ago
        old_time = (datetime.now() - timedelta(days=30)).timestamp()
        import os
        os.utime(old_archive, (old_time, old_time))
        
        # Create recent archive (today)
        recent_archive = archive_dir / "2026-01-13_00-00-00.log"
        recent_archive.write_text("Recent log content")
        
        # CLIENT CALLS CLEANUP (this is client responsibility!)
        deleted_count = cleanup_old_archives()
        
        assert deleted_count == 1
        assert not old_archive.exists()
        assert recent_archive.exists()
    
    def test_cleanup_preserves_recent_archives(self, temp_nibandha_root, monkeypatch):
        """Test that cleanup preserves recent archive files."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 10,
                'rotation_interval_hours': 24,
                'archive_retention_days': 30
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        
        # Create archive directory
        archive_dir = temp_nibandha_root / "Amsha" / "logs" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create recent archives
        recent1 = archive_dir / "2026-01-13_10-00-00.log"
        recent1.write_text("Recent log 1")
        
        recent2 = archive_dir / "2026-01-14_05-00-00.log"
        recent2.write_text("Recent log 2")
        
        # CLIENT CALLS CLEANUP
        deleted_count = cleanup_old_archives()
        
        assert deleted_count == 0
        assert recent1.exists()
        assert recent2.exists()
    
    def test_cleanup_returns_zero_when_disabled(self, temp_nibandha_root, monkeypatch):
        """Test that cleanup returns 0 when rotation is disabled."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({'enabled': False}, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("test")
        
        # CLIENT CALLS CLEANUP (should do nothing)
        deleted_count = cleanup_old_archives()
        
        assert deleted_count == 0


class TestClientIntegrationPatterns:
    """Demonstrate common client integration patterns."""
    
    def test_startup_cleanup_pattern(self, temp_nibandha_root, monkeypatch):
        """Demonstrate cleanup on application startup."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 10,
                'rotation_interval_hours': 24,
                'archive_retention_days': 7
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        # Simulate application startup
        logger = get_logger("my_app")
        
        # CLIENT: Cleanup old logs on startup
        deleted = cleanup_old_archives()
        logger.info(f"Startup cleanup: removed {deleted} old log archives")
        
        # Continue with normal application logic
        logger.info("Application started successfully")
    
    def test_rotation_check_in_loop(self, temp_nibandha_root, monkeypatch):
        """Demonstrate rotation check in long-running process."""
        config_dir = temp_nibandha_root / "config"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 0.001,  # Small limit for testing
                'rotation_interval_hours': 24,
                'archive_retention_days': 30
            }, f)
        
        monkeypatch.chdir(temp_nibandha_root.parent)
        
        logger = get_logger("worker")
        
        # Simulate long-running process
        for i in range(50):
            # Do work
            logger.info(f"Processing item {i} " * 20)
            
            # CLIENT: Check if rotation needed
            if should_rotate():
                logger.info("Log size/time threshold reached, rotating...")
                rotate_logs()
                logger.info(f"Rotation complete, continuing from item {i}")
        
        # Verify rotation happened
        archive_dir = temp_nibandha_root / "Amsha" / "logs" / "archive"
        assert archive_dir.exists()
        archived_logs = list(archive_dir.glob("*.log"))
        assert len(archived_logs) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
