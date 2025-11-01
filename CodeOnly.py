import json
from constraint import Problem, AllDifferentConstraint
from collections import defaultdict


# ==========================================
# Ler ficheiro JSON
# ==========================================
# with open("BigDados.json", "r", encoding="utf-8") as f:
#     dados = json.load(f)
#     print(dados)


def lerDados(filename):
    dados = {"cc" : {}, "olw" : [], "dsd": {}, "tr" : {}, "rr" : {}, "oc" : {}}
    secao = None

    with open(filename, "r", encoding="utf-8") as file:
        for linha in file:
            linha = linha.strip()
            if not linha or linha.startswith("—"):
                continue

            if linha.startswith("#"):
                secao = linha.split()[0][1:]
                continue

            partes = linha.split()

            match secao:
                case "cc":
                    turma, cursos = partes[0], partes[1:]
                    dados["cc"][turma] = cursos
                
                case "olw":
                    if partes:
                        dados["olw"].append(partes[0])
                
                case "dsd":
                    docente, cursos = partes[0], partes[1:]
                    dados["dsd"][docente] = cursos

                case "tr":
                    docente, restricoes = partes[0], list(map(int, partes[1:]))
                    dados["tr"][docente] = restricoes

                case "rr":
                    curso, sala = partes[0], partes[1]
                    dados["rr"][curso] = sala

                case "oc":
                    curso, idx = partes[0], int(partes[1])
                    dados["oc"][curso] = idx

                case _:
                    pass

    return dados


dados = lerDados("ClassTT_01_tiny.txt")
print("A carregar dados")
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

# ==========================================
# Obter primeira solução
# ==========================================

# 1) Variáveis na ordem de criação do python-constraint
variables = list(problem._variables.keys())
TOTAL_BLOCOS = 20
MAX_POR_BLOCO = len(dados["cc"])  # 3 no tiny (1 por turma)

# 2) Mapas auxiliares a partir de 'dados'
def uc_of(var): 
    return var.rsplit("_", 1)[0]

curso_para_turma = {uc: t for t, cursos in dados["cc"].items() for uc in cursos}
curso_para_doc   = {uc: d for d, cursos in dados["dsd"].items() for uc in cursos}
curso_para_sala  = {uc: s for uc, s in dados.get("rr", {}).items()}
docente_indisp   = {d: set(bls) for d, bls in dados.get("tr", {}).items()}

# 3) Consistência (todas as hard constraints)
def is_consistent(assign, var, val):
    uc      = uc_of(var)
    turma   = curso_para_turma.get(uc)
    docente = curso_para_doc.get(uc)
    sala    = curso_para_sala.get(uc)

    # (a) indisponibilidade do docente
    if docente in docente_indisp and val in docente_indisp[docente]:
        return False

    # (b) mesma UC: UC_1 != UC_2
    par = f"{uc}_2" if var.endswith("_1") else f"{uc}_1"
    if par in assign and assign[par] == val:
        return False

    # (c) colisões no mesmo bloco: turma / docente / sala
    total_no_bloco = 0
    turma_no_bloco = False

    for v_assigned, bloco in assign.items():
        if bloco != val:
            continue
        total_no_bloco += 1
        uc2 = uc_of(v_assigned)

        # mesma turma nesse bloco?
        if curso_para_turma.get(uc2) == turma:
            turma_no_bloco = True

        # mesmo docente nesse bloco?
        if docente and curso_para_doc.get(uc2) == docente:
            return False

        # mesma sala fixa nesse bloco?
        if sala and curso_para_sala.get(uc2) == sala:
            return False

    if turma_no_bloco:
        return False  # 1 aula por bloco por turma
    if total_no_bloco >= MAX_POR_BLOCO:
        return False  # capacidade global por bloco

    return True

# 4) Cobertura (usar todos os 20 blocos)
def cobertura_final_ok(assign):
    return len(set(assign.values())) == TOTAL_BLOCOS

def cobertura_ainda_viavel(assign, num_atribuidas):
    # poda segura: não continuar se já for impossível cobrir todos os blocos
    usados = set(assign.values())
    vazios = TOTAL_BLOCOS - len(usados)
    restantes = len(variables) - num_atribuidas
    return restantes >= vazios

# 5) DFS: primeira solução
def dfs_primeira_solucao():
    assign = {}

    def bt(i):
        if i == len(variables):
            return assign.copy() if cobertura_final_ok(assign) else None

        if not cobertura_ainda_viavel(assign, i):
            return None

        var = variables[i]
        for val in blocos:
            if is_consistent(assign, var, val):
                assign[var] = val
                sol = bt(i + 1)
                if sol is not None:
                    return sol
                del assign[var]
        return None

    return bt(0)

# ==========================================
# Transformar em JSON final legível
# ==========================================

print("\nSolução encontrada (DFS):")
solution = dfs_primeira_solucao()

if solution is None:
    print("Nenhuma solução encontrada (DFS).")
else:
    for k in sorted(solution):
        print(f"{k} : {solution[k]}")
