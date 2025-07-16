"""
Event-System für die Kommunikation zwischen Modulen
"""

class EventDispatcher:
    """Einfacher Event-Dispatcher für die Kommunikation zwischen Modulen"""
    
    def __init__(self):
        self.listeners = {}
        
    def add_listener(self, event_name, callback):
        """Fügt einen Event-Listener hinzu"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
        
    def remove_listener(self, event_name, callback):
        """Entfernt einen Event-Listener"""
        if event_name in self.listeners and callback in self.listeners[event_name]:
            self.listeners[event_name].remove(callback)
            
    def dispatch(self, event_name, *args, **kwargs):
        """Löst ein Event aus"""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(*args, **kwargs)

# Globale Event-Dispatcher-Instanz
event_dispatcher = EventDispatcher()