#!/usr/bin/env python3
"""
Tactical RPG 3D Engine - Main Entry Point

This is the main application entry point for the tactical RPG engine.
Implements Phase 1: Foundation according to Advanced-Implementation-Guide.md
"""

import sys
import time
from typing import Dict, Any

# Core imports
from core.ecs.world import World
from core.events.event_bus import EventBus
from core.utils.logging import Logger
from core.utils.performance import PerformanceMonitor

# System imports
from systems.stat_system import StatSystem
from systems.movement_system import MovementSystem

# AI imports  
from ai.mcp.tactical_server import TacticalMCPServer

class TacticalRPGEngine:
    """Main engine class coordinating all game systems"""
    
    def __init__(self):
        self.world = World()
        self.event_bus = EventBus()
        self.performance_monitor = PerformanceMonitor()
        self.mcp_server = None
        self.running = False
        
        # Initialize logging
        Logger.initialize(log_level="INFO")
        Logger.info("Tactical RPG Engine initializing...")
        
    def initialize(self) -> bool:
        """Initialize all engine systems"""
        try:
            # Initialize core systems
            self._initialize_core_systems()
            
            # Initialize game systems
            self._initialize_game_systems()
            
            # Initialize MCP server for AI
            self._initialize_mcp_server()
            
            Logger.info("Engine initialization complete")
            return True
            
        except Exception as e:
            Logger.error(f"Engine initialization failed: {e}")
            return False
    
    def _initialize_core_systems(self):
        """Initialize core engine systems"""
        Logger.info("Initializing core systems...")
        
        # Core systems are already initialized in __init__
        self.performance_monitor.start()
        
    def _initialize_game_systems(self):
        """Initialize game-specific systems"""
        Logger.info("Initializing game systems...")
        
        # Register game systems with world
        self.world.add_system(StatSystem())
        self.world.add_system(MovementSystem())
        
    def _initialize_mcp_server(self):
        """Initialize MCP server for AI integration"""
        Logger.info("Initializing MCP server...")
        
        try:
            self.mcp_server = TacticalMCPServer(world=self.world)
            self.mcp_server.start()
            Logger.info("MCP server started successfully")
        except Exception as e:
            Logger.warning(f"MCP server failed to start: {e}")
            # Continue without MCP - it's not critical for basic functionality
    
    def run(self):
        """Main game loop"""
        Logger.info("Starting main game loop...")
        self.running = True
        
        last_time = time.time()
        target_fps = 60
        frame_time = 1.0 / target_fps
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Update engine
            with self.performance_monitor.measure("frame_update"):
                self._update(delta_time)
            
            # Cap frame rate
            frame_duration = time.time() - current_time
            if frame_duration < frame_time:
                time.sleep(frame_time - frame_duration)
        
        Logger.info("Game loop ended")
    
    def _update(self, delta_time: float):
        """Update all engine systems"""
        
        # Update world (which updates all systems)
        self.world.update(delta_time)
        
        # Process events
        self.event_bus.process_events()
        
        # Update performance monitoring
        self.performance_monitor.update(delta_time)
    
    def shutdown(self):
        """Gracefully shutdown the engine"""
        Logger.info("Shutting down engine...")
        self.running = False
        
        # Shutdown MCP server
        if self.mcp_server:
            self.mcp_server.stop()
        
        # Generate performance report
        report = self.performance_monitor.generate_report()
        Logger.info(f"Performance report: {report}")
        
        Logger.info("Engine shutdown complete")

def main():
    """Main application entry point"""
    engine = TacticalRPGEngine()
    
    if not engine.initialize():
        Logger.error("Failed to initialize engine")
        sys.exit(1)
    
    try:
        engine.run()
    except KeyboardInterrupt:
        Logger.info("Received shutdown signal")
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        engine.shutdown()

if __name__ == "__main__":
    main()