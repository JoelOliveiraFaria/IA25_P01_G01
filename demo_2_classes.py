from constraint import Problem, AllDifferentConstraint

# Cenario explicado:
#   Turma A (curso original) com 4 cadeiras
#       - Algoritmos (Prof. Ana) -> sala fixa Sala A
#       - Matematica (Prof. Ana) -> Sala A ou Laboratorio
#       - Inteligencia Artificial (Prof. Bruno) -> sempre Online
#       - Bases de Dados (Prof. Bruno) -> sempre Laboratorio
#   Turma B (novo curso) com 4 cadeiras
#       - Programacao 1 (Prof. Carla) -> Laboratorio
#       - Visao por Computador (Prof. David) -> Sala B ou Laboratorio
#       - Eletronica (Prof. Eva) -> Sala B
#       - Inteligencia Artificial (Prof. Bruno) -> sempre Online
# As duas turmas podem usar o mesmo bloco horario; apenas evitamos conflitos
# dentro de cada turma e impedimos que um docente tenha duas aulas simultaneas.

BLOCOS = [1, 2, 3, 4]

problema = Problem()

# ---------------- Turma A ----------------
problema.addVariable("intervalo_algoritmos", [1, 3, 4])  # Prof. Ana indisponivel no bloco 2
problema.addVariable("sala_algoritmos", ["Sala A"])

problema.addVariable("intervalo_matematica", BLOCOS)
problema.addVariable("sala_matematica", ["Sala A", "Laboratorio"])

problema.addVariable("intervalo_inteligencia_A", BLOCOS)
problema.addVariable("sala_inteligencia_A", ["Online"])

problema.addVariable("intervalo_bases_dados", BLOCOS)
problema.addVariable("sala_bases_dados", ["Laboratorio"])

# ---------------- Turma B ----------------
problema.addVariable("intervalo_programacao1", BLOCOS)
problema.addVariable("sala_programacao1", ["Laboratorio"])

problema.addVariable("intervalo_visao_computador", BLOCOS)
problema.addVariable("sala_visao_computador", ["Sala B", "Laboratorio"])

problema.addVariable("intervalo_eletronica", BLOCOS)
problema.addVariable("sala_eletronica", ["Sala B"])

problema.addVariable("intervalo_inteligencia_B", BLOCOS)
problema.addVariable("sala_inteligencia_B", ["Online"])

# Conflitos dentro de cada turma
problema.addConstraint(AllDifferentConstraint(), [
    "intervalo_algoritmos",
    "intervalo_matematica",
    "intervalo_inteligencia_A",
    "intervalo_bases_dados",
])

problema.addConstraint(AllDifferentConstraint(), [
    "intervalo_programacao1",
    "intervalo_visao_computador",
    "intervalo_eletronica",
    "intervalo_inteligencia_B",
])

# Restricoes por docente
problema.addConstraint(AllDifferentConstraint(), [
    "intervalo_algoritmos",
    "intervalo_matematica",
])  # Prof. Ana, era necessária esta restrição?

problema.addConstraint(AllDifferentConstraint(), [
    "intervalo_inteligencia_A",
    "intervalo_bases_dados",
    "intervalo_inteligencia_B",
])  # Prof. Bruno


def sem_conflito_sala(intervalo1, sala1, intervalo2, sala2):
    if sala1 == "Online" or sala2 == "Online":
        return True
    if sala1 != sala2:
        return True
    return intervalo1 != intervalo2

# Restricoes de partilha de sala entre turmas
for vars_sala in [
    ("intervalo_matematica", "sala_matematica", "intervalo_programacao1", "sala_programacao1"),             #Laboratório
    ("intervalo_matematica", "sala_matematica", "intervalo_visao_computador", "sala_visao_computador"),     #Laboratório
    ("intervalo_bases_dados", "sala_bases_dados", "intervalo_programacao1", "sala_programacao1"),           #Laboratório
    ("intervalo_bases_dados", "sala_bases_dados", "intervalo_visao_computador", "sala_visao_computador"),   #Laboratório
    ("intervalo_eletronica", "sala_eletronica", "intervalo_visao_computador", "sala_visao_computador"),     #Sala B não era necessária esta R visto que são 2 UCs da mesma turma
]:
    problema.addConstraint(sem_conflito_sala, vars_sala)

# Docentes Carla, David e Eva lecionam apenas uma UC cada.

solucoes = problema.getSolutions()

print(f"Número de soluções possíveis: {len(solucoes)}")

if solucoes:
    melhor = solucoes[0]
    print("Horario Turma A:\n")
    print(
        f"Algoritmos (Prof. Ana) -> bloco {melhor['intervalo_algoritmos']} | "
        f"sala {melhor['sala_algoritmos']}"
    )
    print(
        f"Matematica (Prof. Ana) -> bloco {melhor['intervalo_matematica']} | "
        f"sala {melhor['sala_matematica']}"
    )
    print(
        f"Inteligencia Artificial (Prof. Bruno) -> bloco {melhor['intervalo_inteligencia_A']} | "
        f"sala {melhor['sala_inteligencia_A']}"
    )
    print(
        f"Bases de Dados (Prof. Bruno) -> bloco {melhor['intervalo_bases_dados']} | "
        f"sala {melhor['sala_bases_dados']}"
    )

    print("\nHorario Turma B:\n")
    print(
        f"Programacao 1 (Prof. Carla) -> bloco {melhor['intervalo_programacao1']} | "
        f"sala {melhor['sala_programacao1']}"
    )
    print(
        f"Visao por Computador (Prof. David) -> bloco {melhor['intervalo_visao_computador']} | "
        f"sala {melhor['sala_visao_computador']}"
    )
    print(
        f"Eletronica (Prof. Eva) -> bloco {melhor['intervalo_eletronica']} | "
        f"sala {melhor['sala_eletronica']}"
    )
    print(
        f"Inteligencia Artificial (Prof. Bruno) -> bloco {melhor['intervalo_inteligencia_B']} | "
        f"sala {melhor['sala_inteligencia_B']}"
    )
else:
    print("Nao foi possivel encontrar solucao.")
