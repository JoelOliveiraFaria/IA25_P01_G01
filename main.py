import json
from constraint import Problem, AllDifferentConstraint

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
# Criar variáveis (cada UC tem 1 ou 2 aulas por semana)
# ==========================================
for turma, cursos in dados["cc"].items():
    for curso in cursos:
        if curso not in dados.get("olw", []):
            problem.addVariable(f"{curso}_1", blocos)
            problem.addVariable(f"{curso}_2", blocos)
            problem.addConstraint(lambda x, y: x != y, (f"{curso}_1", f"{curso}_2"))
        else:
            problem.addVariable(f"{curso}_1", blocos)

# ==========================================
# Restrições de professor (um professor não pode dar duas aulas ao mesmo tempo)
# ==========================================
for teacher, cursos in dados["dsd"].items():
    variaveis = []
    for curso in cursos:
        if curso not in dados.get("olw", []):
            variaveis.extend([f"{curso}_1", f"{curso}_2"])
        else:
            variaveis.append(f"{curso}_1")
    if len(variaveis) > 1:
        problem.addConstraint(AllDifferentConstraint(), variaveis)

# ==========================================
# Restrições de indisponibilidade dos professores
# ==========================================
for teacher, indisponiveis in dados.get("tr", {}).items():
    cursos = dados["dsd"].get(teacher, [])
    for curso in cursos:
        if curso not in dados.get("olw", []):
            for i in [1, 2]:
                problem.addConstraint(
                    lambda bloco, indisponiveis=indisponiveis: bloco not in indisponiveis,
                    (f"{curso}_{i}",)
                )
        else:
            problem.addConstraint(
                lambda bloco, indisponiveis=indisponiveis: bloco not in indisponiveis,
                (f"{curso}_1",)
            )

# ==========================================
# Restrições de turmas (cada turma só pode ter uma aula por bloco)
# ==========================================
for turma, cursos in dados["cc"].items():
    variaveis = []
    for curso in cursos:
        if curso not in dados.get("olw", []):
            variaveis.extend([f"{curso}_1", f"{curso}_2"])
        else:
            variaveis.append(f"{curso}_1")
    if len(variaveis) > 1:
        problem.addConstraint(AllDifferentConstraint(), variaveis)

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
    if len(variaveis) > 1:
        problem.addConstraint(AllDifferentConstraint(), variaveis)

# ==========================================
# Obter primeira solução
# ==========================================
solucao = problem.getSolution()

# ==========================================
# Transformar em JSON final legível
# ==========================================
if solucao:
    print("\nSolução encontrada:")
    print(json.dumps(solucao, indent=4))
else:
    print("Nenhuma solução encontrada")
