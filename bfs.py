#BFS NÃO TESTADO, CHATGPT

from collections import deque
import json

def bfs_queue(variables, constraints):
    """
    variables: dicionário {var_name: dominio}
    constraints: lista de constraints
    Retorna a primeira solução válida encontrada (dicionário UC -> bloco)
    """
    # Inicialmente, a queue contém apenas o estado vazio
    queue = deque([{}])  # cada elemento é um dict {UC: bloco}

    variable_keys = list(variables.keys())

    while queue:
        stack = queue.popleft()  # pega o próximo estado da frente da fila

        # Se todas as variáveis estão atribuídas, temos solução
        if checkSolution(variables, stack):
            return stack

        # Determinar a próxima variável a atribuir
        index = len(stack)  # como no DFS, usamos o número de variáveis já atribuídas
        if index >= len(variable_keys):
            continue  # já não há variável para atribuir, mas solução incompleta

        uc = variable_keys[index]
        blocos = variables[uc]

        # Para cada possível valor do domínio
        for bloco in blocos:
            new_stack = stack.copy()  # copia o estado atual
            new_stack[uc] = bloco

            if constraintCheck(new_stack, constraints):
                queue.append(new_stack)  # adiciona ao final da fila

    return None  # nenhuma solução encontrada

# ---- Teste BFS ----
solution_bfs = bfs_queue(variables, constraints)
print("\nSolução encontrada com BFS:")
print(json.dumps(solution_bfs, indent=4))
