# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
ExampleGuardedVault — demo integrator for HaltGate.
Privileged actions revert while is_halted(target_id) is true.
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
    haltgate_addr: Address
    target_id: str
    acts: u256

    def __init__(self, haltgate_addr: str, target_id: str):
        self.haltgate_addr = Address(haltgate_addr)
        tid = (target_id or "").strip()
        require(1 <= len(tid) <= 64, "bad target_id")
        self.target_id = tid
        self.acts = u256(0)

    def _ensure_not_halted(self) -> None:
        hg = gl.get_contract_at(self.haltgate_addr)
        halted = hg.view().is_halted(self.target_id)
        require(halted is not True, "target halted by HaltGate")

    @gl.public.write
    def act(self) -> str:
        self._ensure_not_halted()
        self.acts = self.acts + u256(1)
        return "ok"

    @gl.public.write
    def withdraw(self) -> str:
        self._ensure_not_halted()
        return "withdraw_ok"

    @gl.public.view
    def status(self) -> str:
        hg = gl.get_contract_at(self.haltgate_addr)
        halted = hg.view().is_halted(self.target_id)
        if halted is True:
            return "FROZEN"
        return "ACTIVE"

    @gl.public.view
    def get_target_id(self) -> str:
        return self.target_id

    @gl.public.view
    def get_haltgate(self) -> Address:
        return self.haltgate_addr

    @gl.public.view
    def get_acts(self) -> u256:
        return self.acts