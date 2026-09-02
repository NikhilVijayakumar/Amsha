"""
Crew monitoring for Amsha: OS-level resource sampling (CrewPerformanceMonitor)
plus CrewAI event-bus observability (AmshaEventListener).
"""

from amsha.crew_monitor.service.amsha_event_listener import AmshaEventListener

# CrewAI footgun: a BaseEventListener subclass is only alive while referenced.
# Hold a module-level instance so event handlers fire for the whole process
# without consumers having to remember to keep it alive.
_event_listener = AmshaEventListener()

__all__ = ["AmshaEventListener"]