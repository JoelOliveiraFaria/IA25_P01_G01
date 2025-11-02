import json
from constraint import Problem, AllDifferentConstraint
from collections import deque
import matplotlib.pyplot as plt

# ==========================================
# Ler ficheiro JSON
# ==========================================
with open("BigDados.json", "r", encoding="utf-8") as f:
    dados = json.load(f)
    print(dados)

# Inicializar problema CSP
problem = Problem()
blocos = list(range(1, 21))  # 20 blocos semanais

# ==========================================
# Criar variáveis (cada UC tem 1(olw) ou 2 aulas por semana)
# ==========================================
for turma, cursos in dados["cc"].items():
    for curso in cursos:
        if curso not in dados.get("olw", []):
            problem.addVariable(f"{curso}_1", blocos)
            problem.addVariable(f"{curso}_2", blocos)
            problem.addConstraint(lambda x, y: x != y, (f"{curso}_1", f"{curso}_2")) # Garantir que as duas aulas são em blocos diferentes
        else:
            problem.addVariable(f"{curso}_1", blocos) #UC Owls têm apenas 1 aula por semana

# ==========================================
# Restrições de professor (um professor não pode dar duas aulas ao mesmo tempo)
# ==========================================
for docente, cursos in dados["dsd"].items():
    variaveis = []
    for curso in cursos:    #array com todas UCs de um docente UC_1 e UC_2 ou apenas UC_1 se for owl
        if curso not in dados.get("olw", []):
            variaveis.extend([f"{curso}_1", f"{curso}_2"])
        else:
            variaveis.append(f"{curso}_1")
    problem.addConstraint(AllDifferentConstraint(), variaveis) # Constraint para que não tenha UCs repetidas

# ==========================================
# Restrições de indisponibilidade dos professores
# ==========================================
for docente, indisponiveis in dados.get("tr", {}).items():
    cursos = dados["dsd"].get(docente, []) #UCs do docente
    for curso in cursos:
        if curso not in dados.get("olw", []):
            for i in [1, 2]:
                problem.addConstraint(
                    lambda bloco, indisponiveis=indisponiveis: bloco not in indisponiveis, #Bloco = variável , indisponiveis = lista de blocos indisponiveis (Dominio da variável)
                    (f"{curso}_{i}",)
                )
        else:
            problem.addConstraint(
                lambda bloco, indisponiveis=indisponiveis: bloco not in indisponiveis, #Compara UC_x com blocos indisponiveis para o docente que leciona a UC
                (f"{curso}_1",)
            )

# ==========================================
# Restrições de turmas (cada turma só pode ter uma aula por bloco)
# ==========================================
for turma, cursos in dados["cc"].items():
    variaveis = []
    for curso in cursos:    #array com todas UCs de uma turma UC_1 e UC_2 ou apenas UC_1 se for owl
        if curso not in dados.get("olw", []):
            variaveis.extend([f"{curso}_1", f"{curso}_2"])
        else:
            variaveis.append(f"{curso}_1")
    problem.addConstraint(AllDifferentConstraint(), variaveis) # Constraint para que não tenha UCs repetidas

# ==========================================
# Restrições de sala (apenas para UCs com sala atribuída)
# ==========================================
salas = {}

for curso, sala in dados.get("rr", {}).items():
    if sala not in salas:
        salas[sala] = []
    if curso not in dados.get("olw", []):
        salas[sala].extend([f"{curso}_1", f"{curso}_2"])
    else:
        salas[sala].append(f"{curso}_1")

# Cada sala só pode ter uma aula por bloco
for sala, variaveis in salas.items():
    problem.addConstraint(AllDifferentConstraint(), variaveis) # Constraint para que não tenha UCs com a mesma sala não tenham o mesmo bloco


# ==============================================
# Visualização do problema
# ==============================================

def plot_schedule(solution, title="Horário"):
    # Dias e horas
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    blocos_horas = ["09-11h", "11-13h", "14-16h", "16-18h"]

    # Cria matriz 4x5 (4 blocos por dia × 5 dias)
    grid = [[[] for _ in range(5)] for _ in range(4)]

    for uc, bloco in solution.items():
        bloco -= 1
        dia = bloco // 4          # coluna (x)
        slot = bloco % 4          # linha (y)
        grid[slot][dia].append(uc)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(title, fontsize=14, fontweight="bold")

    ax.set_xticks(range(5))
    ax.set_xticklabels(dias, fontsize=10)

    ax.set_yticks(range(4))
    ax.set_yticklabels(blocos_horas, fontsize=10)

    # Desenha o grid e escreve UCs
    for y in range(4):
        for x in range(5):
            rect = plt.Rectangle((x, y), 1, 1, fill=False)
            ax.add_patch(rect)
            cell_text = "\n".join(grid[y][x])
            ax.text(
                x + 0.5, y + 0.5, cell_text,
                ha="center", va="center", fontsize=8, wrap=True
            )

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 4)
    ax.invert_yaxis()  # 09h em cima
    plt.tight_layout()
    plt.show()

# ==========================================
# Converter Problem() para Variaveis e Restrições
# ==========================================

variables = problem._variables
domain = blocos
constraints = problem._constraints

timeslot_constraints = {}

for docente, cursos in dados["dsd"].items():
    indisponiveis = dados["tr"].get(docente, [])
    for curso in cursos:
        timeslot_constraints[curso] = indisponiveis


""" print("\nteste var\n")                                                          #CONVERÇÃO: Problem() para Variaveis e Restrições
print(variaveis)

print("\nteste cons")
print(constraints)

print("\nteste cons2")
print(constraints[0][1]) """                                                        #Constraints (Tipo de constraint, [UCs envolvidas na constraint])

# ==========================================
# Funções de verificação
# ==========================================

def checkSolution(variables, stack):
    # Verifica se todas as variáveis têm valores atribuídos
    for uc in variables.keys():
        if uc not in stack.keys():
            return False
    return True
    
def constraintCheck(stack, constraints):
    # Verifica se o stack atual satisfaz todas as constraints
    for constraint, uc_in_constraint in constraints:
        if isinstance(constraint, AllDifferentConstraint): #Verifica todas as constraints do tipo AllDifferentConstraint, para turmas, professores e salas
            valores = [] #lista de valores já atribuídos às UCs na constraint
            for uc in uc_in_constraint: #para cada UC na AllDifferentConstraint
                if uc in stack: #verifica se a UC está no stack atual
                    valor = stack[uc] #pega o valor atribuído à UC no stack
                    if valor in valores: #se o valor já estiver na lista de valores, falha pois um outra UC anterior já tem esse valor
                        return False
                    valores.append(valor) #se o valor não estiver na lista, adiciona-o

    #Verifica as restrições de indisponibilidade dos professores
    for uc, bloco in stack.items():
            uc_base = uc.split("_")[0]  # pega 'UC11' de 'UC11_1'
            if bloco in timeslot_constraints.get(uc_base, []):
                return False
    return True

# ==========================================
# DFS com stack (recursivo)
# ==========================================

def dfs_recursive_stack(variables, constraints, stack, index):
    """
    variables: dicionário {var_name: dominio}
    constraints: lista de constraints
    stack: dicionário {UC: bloco} representando o caminho atual
    index: índice da próxima variável a explorar
    """
    # se todas as variáveis estão atribuídas, retornamos a solução
    if checkSolution(variables, stack):
        return stack

    uc = list(variables.keys())[index]

    # pegar a próxima variável que ainda não está no stack
    blocos = variables[uc]
    for bloco in blocos:
        stack[uc] = bloco  # atribuir valor à variável
        if constraintCheck(stack, constraints): #true continua, false backtrack
            solution = dfs_recursive_stack(variables, constraints, stack, index+1)
            if solution is not None:
                return solution # encontrou solução, desfaz a recursão
        stack.pop(uc)  # backtrack caso falha a constraintCheck ou não encontrou solução adiante
            
    return None  # nenhum valor válido


solution = dfs_recursive_stack(variables, constraints, {}, 0)

if solution:
    print(json.dumps(solution, indent=4))
    plot_schedule(solution, title="Horário gerado DFS")
else:
    print("Nenhuma solução encontrada")



# ==========================================
# BFS com fila
# ==========================================


def bfs_level_by_level(variables, constraints):
    queue = deque()
    queue.append({})  # stack inicial (vazia)

    variable_keys = list(variables.keys())

    while queue:
        stack = queue.popleft()   # tira 1 caminho parcial

        # Se a stack já é uma solução completa
        if checkSolution(variables, stack):
            return stack  

        # Determinar qual UC atribuir a seguir
        next_var_index = len(stack)
        uc = variable_keys[next_var_index]

        # Expandir este ramo com todos os blocos possíveis
        for bloco in variables[uc]:
            new_stack = stack.copy()
            new_stack[uc] = bloco

            # Só colocamos na fila se respeita as restrições
            if constraintCheck(new_stack, constraints):
                queue.append(new_stack)

    return None  # sem solução

# ---- Teste BFS ----
solution_bfs = bfs_level_by_level(variables, constraints)
if solution_bfs:
    print(json.dumps(solution_bfs, indent=4))
    plot_schedule(solution_bfs, title="Horário gerado BFS")
else:
    print("Nenhuma solução encontrada")




