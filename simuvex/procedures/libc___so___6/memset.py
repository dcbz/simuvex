import simuvex
from simuvex.s_type import SimTypeTop, SimTypeInt, SimTypeLength

import logging
l = logging.getLogger("simuvex.procedures.libc.memset")

######################################
# memset
######################################

class memset(simuvex.SimProcedure):
	def __init__(self): # pylint: disable=W0231
		dst_addr = self.arg(0)
		char = self.arg(1)[7:0]
		num = self.arg(2)

		self.argument_types = {0: self.ty_ptr(SimTypeTop()),
				       1: SimTypeInt(32, True), # ?
				       2: SimTypeLength(self.state.arch)}
		self.return_type = self.ty_ptr(SimTypeTop())

		if self.state.se.symbolic(num):
			l.debug("symbolic length")
			max_size = self.state.se.min_int(num) + self.state['libc'].max_buffer_size
			write_bytes = self.state.se.Concat(*([ char ] * max_size))
			self.state.store_mem(dst_addr, write_bytes, symbolic_length=num)
		else:
			max_size = self.state.se.any_int(num)
			write_bytes = self.state.se.Concat(*([ char ] * max_size))
			self.state.store_mem(dst_addr, write_bytes)

			l.debug("memset writing %d bytes", max_size)

		self.add_refs(simuvex.SimMemWrite(self.addr, self.stmt_from, dst_addr, write_bytes, max_size*8, [], [], [], []))
		self.ret(dst_addr)