"""fleet-ops: small operations service on top of the UAV Defense Simulator.

It reads telemetry frames from the simulator backend (or from a sample file
when running disconnected), estimates battery time remaining, and raises
alerts for aircraft that cannot make it back to base.
"""
__version__ = "0.3.1"
