"""
Animation System - Smooth animations for UI components.
"""

import math
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class EasingType(Enum):
    """Animation easing types."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class Animation:
    """Individual animation instance."""
    
    def __init__(
        self,
        target: Any,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None,
        delay: float = 0.0
    ):
        self.target = target
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = easing
        self.on_complete = on_complete
        self.delay = delay
        
        self.elapsed_time = 0.0
        self.is_complete = False
        self.is_started = False
    
    def update(self, dt: float) -> None:
        """Update animation progress."""
        if self.is_complete:
            return
        
        self.elapsed_time += dt
        
        # Handle delay
        if not self.is_started:
            if self.elapsed_time >= self.delay:
                self.is_started = True
                self.elapsed_time = 0.0
            else:
                return
        
        # Calculate progress
        progress = min(self.elapsed_time / self.duration, 1.0)
        eased_progress = self._apply_easing(progress)
        
        # Update property
        current_value = self.start_value + (self.end_value - self.start_value) * eased_progress
        setattr(self.target, self.property_name, current_value)
        
        # Check completion
        if progress >= 1.0:
            self.is_complete = True
            if self.on_complete:
                self.on_complete()
    
    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress."""
        if self.easing == EasingType.LINEAR:
            return t
        elif self.easing == EasingType.EASE_IN:
            return t * t
        elif self.easing == EasingType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif self.easing == EasingType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif self.easing == EasingType.BOUNCE:
            if t < 1/2.75:
                return 7.5625 * t * t
            elif t < 2/2.75:
                t -= 1.5/2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5/2.75:
                t -= 2.25/2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625/2.75
                return 7.5625 * t * t + 0.984375
        elif self.easing == EasingType.ELASTIC:
            if t == 0 or t == 1:
                return t
            return -(2**(-10 * t)) * math.sin((t - 0.1) * (2 * math.pi) / 0.4) + 1
        
        return t


class AnimationSystem:
    """Manages all animations in the application."""
    
    def __init__(self):
        self.animations: List[Animation] = []
        self.paused = False
    
    def animate(
        self,
        target: Any,
        property_name: str,
        end_value: float,
        duration: float,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None,
        delay: float = 0.0
    ) -> Animation:
        """Start a new animation."""
        start_value = getattr(target, property_name, 0.0)
        
        animation = Animation(
            target=target,
            property_name=property_name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
            on_complete=on_complete,
            delay=delay
        )
        
        self.animations.append(animation)
        return animation
    
    def animate_to(
        self,
        target: Any,
        properties: Dict[str, float],
        duration: float,
        easing: EasingType = EasingType.EASE_OUT,
        on_complete: Optional[Callable] = None,
        delay: float = 0.0
    ) -> List[Animation]:
        """Animate multiple properties simultaneously."""
        animations = []
        
        for prop_name, end_value in properties.items():
            animation = self.animate(
                target=target,
                property_name=prop_name,
                end_value=end_value,
                duration=duration,
                easing=easing,
                delay=delay
            )
            animations.append(animation)
        
        # Set completion callback on the last animation
        if animations and on_complete:
            animations[-1].on_complete = on_complete
        
        return animations
    
    def stop_animations(self, target: Any, property_name: Optional[str] = None) -> None:
        """Stop animations for a target."""
        to_remove = []
        
        for animation in self.animations:
            if animation.target == target:
                if property_name is None or animation.property_name == property_name:
                    to_remove.append(animation)
        
        for animation in to_remove:
            self.animations.remove(animation)
    
    def update(self, dt: float) -> None:
        """Update all animations."""
        if self.paused:
            return
        
        completed_animations = []
        
        for animation in self.animations:
            animation.update(dt)
            if animation.is_complete:
                completed_animations.append(animation)
        
        # Remove completed animations
        for animation in completed_animations:
            self.animations.remove(animation)
    
    def pause(self) -> None:
        """Pause all animations."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume all animations."""
        self.paused = False
    
    def clear(self) -> None:
        """Clear all animations."""
        self.animations.clear()
    
    def get_animation_count(self) -> int:
        """Get number of active animations."""
        return len(self.animations)


# Global animation system instance
animation_system = AnimationSystem()


# Convenience functions
def animate(target: Any, property_name: str, end_value: float, duration: float, **kwargs) -> Animation:
    """Convenience function to start an animation."""
    return animation_system.animate(target, property_name, end_value, duration, **kwargs)

def animate_to(target: Any, properties: Dict[str, float], duration: float, **kwargs) -> List[Animation]:
    """Convenience function to animate multiple properties."""
    return animation_system.animate_to(target, properties, duration, **kwargs)

def stop_animations(target: Any, property_name: Optional[str] = None) -> None:
    """Convenience function to stop animations."""
    animation_system.stop_animations(target, property_name)