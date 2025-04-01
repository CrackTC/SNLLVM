jal _start
nop
li $v0, 10
syscall
nop

_read_char:
	li $v0, 12
	syscall
	jr $ra
	nop

_read_int:
	li $v0, 5
	syscall
	jr $ra
	nop

_write_char:
	li $v0, 11
	syscall
	jr $ra
	nop

_write_int:
	li $v0, 1
	syscall
	jr $ra
	nop
