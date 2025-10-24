from constraint import Problem, AllDifferentConstraint
from collections import defaultdict

# --------------------------
# Dados do problema (dataset)
# --------------------------

# Classes e UCs (cada UC tem 2 aulas/semana, não há #olw)
classes_courses = {
    "t01": ["UC11", "UC12", "UC13", "UC14", "UC15"],
    "t02": ["UC21", "UC22", "UC23", "UC24", "UC25"],
    "t03": ["UC31", "UC32", "UC33", "UC34", "UC35"],
}

# Docentes por UC
teacher_courses = {
    "jo":   ["UC11", "UC21", "UC22", "UC31"],
    "mike": ["UC12", "UC23", "UC32"],
    "rob":  ["UC13", "UC14", "UC24", "UC33"],
    "sue":  ["UC15", "UC25", "UC34", "UC35"],
}

# Indisponibilidades de docentes (slots indisponíveis)
teacher_unavailable = {
    "mike": set(range(13, 21)),             # 13..20
    "rob":  set([1, 2, 3, 4]),               # 1..4
    "sue":  set([9, 10, 11, 12, 17, 18, 19, 20]),
    # "jo" sem restrições explícitas
}

# Restrições de sala (curso -> sala obrigatória)
room_requirements = {
    "UC14": "Lab01",
    "UC22": "Lab01",
}

# Aulas online (curso -> conjunto de índices de aula online)
# Ex.: índice 1 e 2 representam as duas aulas semanais de cada UC
online_lessons = {
    "UC21": {2},
    "UC31": {2},
}

# -------------
# Utilitários
# -------------

ALL_SLOTS = list(range(1, 21))  # 1..20
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def slot_to_day(slot):
    # slot 1..4 -> Mon, 5..8 -> Tue, 9..12 -> Wed, 13..16 -> Thu, 17..20 -> Fri
    return (slot - 1) // 4  # 0..4

def day_name(slot):
    return DAYS[slot_to_day(slot)]

def block_in_day(slot):
    return ((slot - 1) % 4) + 1  # 1..4

# Mapas auxiliares
course_teacher = {}
for t, courses in teacher_courses.items():
    for c in courses:
        course_teacher[c] = t

course_class = {}
for cl, courses in classes_courses.items():
    for c in courses:
        course_class[c] = cl

all_courses = [c for courses in classes_courses.values() for c in courses]

# Todas as UCs com 2 aulas por semana (olw vazio)
lessons_per_course = {c: 2 for c in all_courses}

# ---------------------------------------
# Construção do problema de restrições
# ---------------------------------------

problem = Problem()

# Variáveis: para cada UC e cada aula (1..2), escolher um slot 1..20
# Domínio já filtra indisponibilidades do docente responsável por cada UC
for c in all_courses:
    teacher = course_teacher[c]
    unavailable = teacher_unavailable.get(teacher, set())
    allowed = [s for s in ALL_SLOTS if s not in unavailable]
    for k in range(1, lessons_per_course[c] + 1):
        var = f"{c}_{k}"
        problem.addVariable(var, allowed)

# -------------------
# Restrições duras
# -------------------

# 1) Aulas da mesma UC em slots distintos
for c in all_courses:
    vars_uc = [f"{c}_{k}" for k in range(1, lessons_per_course[c] + 1)]
    if len(vars_uc) > 1:
        problem.addConstraint(AllDifferentConstraint(), vars_uc)

# 2) Uma turma não pode ter duas aulas no mesmo slot
for cl, courses in classes_courses.items():
    vars_class = []
    for c in courses:
        vars_class.extend([f"{c}_{k}" for k in range(1, lessons_per_course[c] + 1)])
    # Todas as 10 aulas da turma tXX em slots diferentes
    problem.addConstraint(AllDifferentConstraint(), vars_class)

# 3) Um docente não pode lecionar duas aulas no mesmo slot
for t, courses in teacher_courses.items():
    vars_teacher = []
    for c in courses:
        vars_teacher.extend([f"{c}_{k}" for k in range(1, lessons_per_course[c] + 1)])
    if len(vars_teacher) > 1:
        problem.addConstraint(AllDifferentConstraint(), vars_teacher)

# 4) Recurso Lab01 exclusivo por slot (UC14 e UC22)
lab_courses = [c for c, r in room_requirements.items() if r == "Lab01"]
lab_vars = []
for c in lab_courses:
    for k in range(1, lessons_per_course[c] + 1):
        # Se um dia houver UC com aula online + Lab, ignorar os índices online
        if c in online_lessons and k in online_lessons[c]:
            continue
        lab_vars.append(f"{c}_{k}")
if len(lab_vars) > 1:
    problem.addConstraint(AllDifferentConstraint(), lab_vars)

# 5) (Opcional conforme guia) Máximo 3 aulas por dia por turma
#     Esta regra ajuda a manter cargas diárias razoáveis.
def max_three_per_day(*slots):
    # slots é a lista de 10 valores (uma turma tem 5 UCs x 2 aulas)
    count_by_day = defaultdict(int)
    for s in slots:
        d = slot_to_day(s)
        count_by_day[d] += 1
        if count_by_day[d] > 3:
            return False
    return True

for cl, courses in classes_courses.items():
    vars_class = []
    for c in courses:
        vars_class.extend([f"{c}_{k}" for k in range(1, lessons_per_course[c] + 1)])
    problem.addConstraint(max_three_per_day, vars_class)

# -------------------
# Resolução
# -------------------
solution = problem.getSolution()

if solution is None:
    print("Nenhuma solução encontrada.")
else:
    # Impressão do horário por turma
    print("===== Horário por Turma =====")
    for cl, courses in classes_courses.items():
        items = []
        for c in courses:
            for k in range(1, lessons_per_course[c] + 1):
                s = solution[f"{c}_{k}"]
                items.append((s, c, k))
        items.sort(key=lambda x: x[0])
        print(f"\nTurma {cl}:")
        for s, c, k in items:
            t = course_teacher[c]
            room = "ONLINE" if (c in online_lessons and k in online_lessons[c]) else room_requirements.get(c, "Room")
            print(f"  Slot {s:02d} ({day_name(s)} B{block_in_day(s)}): {c} [aula {k}] — prof. {t} — {room}")

    # Impressão do horário por docente
    print("\n===== Horário por Docente =====")
    teacher_schedule = defaultdict(list)
    for c in all_courses:
        t = course_teacher[c]
        for k in range(1, lessons_per_course[c] + 1):
            s = solution[f"{c}_{k}"]
            cl = course_class[c]
            room = "ONLINE" if (c in online_lessons and k in online_lessons[c]) else room_requirements.get(c, "Room")
            teacher_schedule[t].append((s, c, k, cl, room))
    for t, entries in teacher_schedule.items():
        entries.sort(key=lambda x: x[0])
        print(f"\nDocente {t}:")
        for s, c, k, cl, room in entries:
            print(f"  Slot {s:02d} ({day_name(s)} B{block_in_day(s)}): {c} [aula {k}] — turma {cl} — {room}")

    # Impressão dos slots de Lab01 para ver possíveis conflitos
    print("\n===== Uso da Lab01 =====")
    lab_use = []
    for c in lab_courses:
        for k in range(1, lessons_per_course[c] + 1):
            if c in online_lessons and k in online_lessons[c]:
                continue
            s = solution[f"{c}_{k}"]
            lab_use.append((s, c, k))
    lab_use.sort(key=lambda x: x[0])
    for s, c, k in lab_use:
        print(f"  Slot {s:02d} ({day_name(s)} B{block_in_day(s)}): {c} [aula {k}] -> Lab01")