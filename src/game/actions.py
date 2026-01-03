from dataclasses import dataclass

@dataclass
class Actions:
    movex: int = 0
    punch: bool = False
    kick: bool = False
    block: bool = False

