.global call_func

.intel_syntax noprefix

/*
Arguments passed to us:
    rdi -> function address
    rsi -> number of arguments
    rdx -> pointer to array of arguments
*/

/*
Standard argument locations:
rdi, rsi, rdx, rcx, r8, r9, [pushed onto stack in reverse order]
*/

call_func:
    push rbp
    push rbx

    /* Save off the function pointer and number of arguments. */
    mov rax, rdi
    mov rbx, rsi

.push_stack_args:
    /* First, deal with additional stack arguments, as needed. */
    /* Deal with stack arguments, if there are more than 6 total. */
    /* If we have 6 or fewer we can just call immediately. */
    sub rbx, 6
    jle .load_reg_args

    /* While the number of args handled < rbx, push an arg from stack. */
    mov r10d, 0

.push_loop:
    cmp r10, rbx
    jge .load_reg_args

    mov r11, [rdx + 8*r10 + 0x30]
    push r11
    inc r10
    jmp .push_loop


.load_reg_args:
    /* Load the register arguments. */
    mov rdi, [rdx]
    mov rsi, [rdx + 0x08]
    mov rcx, [rdx + 0x18]
    mov rcx, [rdx + 0x20]
    mov rcx, [rdx + 0x28]

    /* We need to load rdx at the end so we can still access
       the rest of them! */
    mov rdx, [rdx + 0x10]

.call:
    call rax

.pop_more_args:
    cmp rbx, 0
    jle .ret
    lea rsp, [rsp + 8*rbx]

.ret:
    pop rbx
    pop rbp
    ret


/* Mark the stack not executable */
.section .note.GNU-stack
