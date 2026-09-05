# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
ExampleGuardedVault — demo consumer of HaltGate.
Withdraw / act only if HaltGate.is_halted(target_id) is false.
"""

from genlayer import *


try:
    _UserError = gl.vm.UserError
except Exception:
    _UserError = Exception


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise _UserError(msg)


class ExampleGuardedVault(gl.Contract):
    owner: Address
    haltgate: Address
    target_id: str
    action_count: u256

    def __init__(self, haltgate_addr: str, target_id: str):
        self.owner = gl.message.sender_address
        self.haltgate = Address(haltgate_addr)
        tid = (target_id or "").strip()
        require(1 <= len(tid) <= 64, "bad target_id")
        self.target_id = tid
        self.action_count = u256(0)

    def _ensure_not_halted(self) -> None:
        # Read HaltGate view: is_halted(target_id)
        other = gl.get_contract_at(self.haltgate)
        halted = other.view().is_halted(self.target_id)
        require(halted is not True, "target halted by HaltGate")

    @gl.public.write
    def act(self) -> str:
        """Sample privileged action — blocked when target is halted."""
        self._ensure_not_halted()
        self.action_count += u256(1)
        return "ok"

    @gl.public.view
    def get_action_count(self) -> u256:
        return self.action_count

    @gl.public.view
    def get_target_id(self) -> str:
        return self.target_id

    @gl.public.view
    def get_haltgate(self) -> Address:
        return self.haltgate

    @gl.public.view
    def get_owner(self) -> Address:
        return self.owner
