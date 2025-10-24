import json
from constraint import Problem, AllDifferentConstraint


# ==========================================
# Ler ficheiro JSON
# ==========================================
with open("BigDados.json", "r", encoding="utf-8") as f:
    dados = json.load(f)


# ==========================================
# Extrair dados
# ==========================================
BLOCOS = list(range(1, dados["head"]["blocks"] + 1))
LESSONS_PER_WEEK = dados["head"]["lessons_per_week"]

turmas = dados["cc"]
docentes = dados["dsd"]
restricoes_tempo = dados["tr"]
salas_fixas = dados.get("rr", {})
aulas_online = dados.get("oc", {})


# ==========================================
# Extrair TODAS as UCs
# ==========================================
todas_ucs = set()
for turma, ucs in turmas.items():
    todas_ucs.update(ucs)
for docente, ucs in docentes.items():
    todas_ucs.update(ucs)
todas_ucs = sorted(todas_ucs)


# ==========================================
# Função para calcular blocos disponíveis
# ==========================================
def blocos_disponiveis_para_uc(uc, docentes, restricoes_tempo):
    """
    Retorna lista de blocos disponíveis para uma UC,
    removendo blocos indisponíveis do docente.
    """
    # Encontra o docente que leciona esta UC
    docente_uc = None
    for doc, ucs_doc in docentes.items():
        if uc in ucs_doc:
            docente_uc = doc
            break
    
    # Se o docente tem restrições de tempo, filtra os blocos
    if docente_uc and docente_uc in restricoes_tempo:
        indisponiveis = restricoes_tempo[docente_uc]
        return [b for b in BLOCOS if b not in indisponiveis]
    
    # Caso contrário, retorna todos os blocos
    return BLOCOS


# ==========================================
# Função para determinar a sala de uma aula
# ==========================================
def obter_sala(uc, numero_aula):
    """
    Retorna a sala onde a aula será lecionada.
    - Se UC tem sala fixa (rr), usa essa sala
    - Se a aula específica é online (oc), retorna "Online"
    - Caso contrário, retorna "Sala Geral"
    """
    # Verifica se esta aula específica é online
    if uc in aulas_online and aulas_online[uc] == numero_aula:
        return "Online"
    
    # Verifica se a UC tem sala fixa
    if uc in salas_fixas:
        return salas_fixas[uc]
    
    # Caso contrário, sala geral
    return "Sala Geral"


# ==========================================
# Criar problema
# ==========================================
problema = Problem()

# Variáveis: cada UC tem LESSONS_PER_WEEK aulas semanais
# COM DOMÍNIOS REDUZIDOS (otimização)
for uc in todas_ucs:
    blocos_uc = blocos_disponiveis_para_uc(uc, docentes, restricoes_tempo)
    for i in range(1, LESSONS_PER_WEEK + 1):
        problema.addVariable(f"{uc}_L{i}", blocos_uc)


# ==========================================
# CONSTRAINTS
# ==========================================

# 1️⃣ — Evitar sobreposição dentro da mesma turma
for turma, ucs in turmas.items():
    variaveis_turma = [f"{uc}_L{i}" for uc in ucs for i in range(1, LESSONS_PER_WEEK + 1)]
    problema.addConstraint(AllDifferentConstraint(), variaveis_turma)


# 2️⃣ — Evitar sobreposição de aulas de docentes
for docente, ucs in docentes.items():
    variaveis_docente = [f"{uc}_L{i}" for uc in ucs for i in range(1, LESSONS_PER_WEEK + 1)]
    problema.addConstraint(AllDifferentConstraint(), variaveis_docente)


# 3️⃣ — Respeitar indisponibilidades
def disponivel(slot, indisponiveis):
    return slot not in indisponiveis


for docente, indisponiveis in restricoes_tempo.items():
    for uc in docentes[docente]:
        for i in range(1, LESSONS_PER_WEEK + 1):
            problema.addConstraint(
                lambda slot, ind=indisponiveis: disponivel(slot, ind),
                [f"{uc}_L{i}"],
            )


# ==========================================
# Resolver - USAR getSolution() EM VEZ DE getSolutions()
# ==========================================
print("A procurar solução...")
solucao = problema.getSolution()

if solucao:
    print("Solução encontrada!\n")
    print("=" * 70)
    
    for turma, ucs in turmas.items():
        print(f"\n📅 HORÁRIO {turma.upper()}")
        print("-" * 70)
        for uc in ucs:
            print(f"\n  {uc}:")
            for i in range(1, LESSONS_PER_WEEK + 1):
                bloco = solucao[f"{uc}_L{i}"]
                sala = obter_sala(uc, i)
                print(f"    Aula {i}: Bloco {bloco:2d} | Sala: {sala}")
        print()
    
    # Mostrar estatísticas dos docentes
    print("\n" + "=" * 70)
    print("📋 DISTRIBUIÇÃO POR DOCENTE")
    print("=" * 70)
    
    for docente, ucs in docentes.items():
        print(f"\n👤 {docente.upper()}")
        print("-" * 70)
        
        blocos_indisponiveis = restricoes_tempo.get(docente, [])
        if blocos_indisponiveis:
            print(f"  ⚠️  Indisponível nos blocos: {blocos_indisponiveis}")
            print()
        
        for uc in ucs:
            print(f"  {uc}:")
            for i in range(1, LESSONS_PER_WEEK + 1):
                bloco = solucao[f"{uc}_L{i}"]
                sala = obter_sala(uc, i)
                print(f"    Aula {i}: Bloco {bloco:2d} | Sala: {sala}")
    
    # Resumo de salas fixas e online
    print("\n" + "=" * 70)
    print("📍 RESUMO DE SALAS ESPECIAIS")
    print("=" * 70)
    
    if salas_fixas:
        print("\n🔒 Salas Fixas:")
        for uc, sala in salas_fixas.items():
            print(f"  {uc} → {sala} (todas as aulas)")
    
    if aulas_online:
        print("\n💻 Aulas Online:")
        for uc, num_aula in aulas_online.items():
            print(f"  {uc} → Aula {num_aula}")
    
    print("\n" + "=" * 70)
    
else:
    print(" Nenhuma solução encontrada.")
    print("\n Possíveis causas:")
    print("  • Restrições muito apertadas (muitas indisponibilidades)")
    print("  • Não há blocos suficientes para todas as aulas")
    print("  • Conflito entre restrições de turmas e docentes")
