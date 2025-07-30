
CAMPOS_POKEMON = [
    "Nome",
    "Vida", "Atk", "Def", "SpA", "SpD", "Vel",
    "Mag", "Per", "Ene", "EnR", "CrD", "CrC",
    "Sinergia", "Habilidades", "Equipaveis", "Total",
    "Poder R1", "Poder R2", "Poder R3",
    "Tipo1", "%1", "Tipo2", "%2", "Tipo3", "%3",
    "Altura", "Peso", "Raridade", "Estagio", "FF", "Code",
    "Nivel",
    "IV",
    "IV_Vida", "IV_Atk", "IV_Def", "IV_SpA", "IV_SpD", "IV_Vel",
    "IV_Mag", "IV_Per", "IV_Ene", "IV_EnR", "IV_CrD", "IV_CrC"
]

def desserializar_pokemon(string):
    partes = string.split(",")
    info = {}
    for i, campo in enumerate(CAMPOS_POKEMON):
        if i < len(partes):
            valor = partes[i].replace(";", ",")  # reverter a substituição
            # Pode converter tipos numéricos aqui se quiser, exemplo:
            if campo in ["Vida", "Atk", "Def", "SpA", "SpD", "Vel",
                         "Mag", "Per", "Ene", "EnR", "CrD", "CrC",
                         "Sinergia", "Habilidades", "Equipaveis", "Total",
                         "Estagio", "Code", "Nivel"]:
                try:
                    valor = int(valor)
                except:
                    pass
            elif campo in ["Poder R1", "Poder R2", "Poder R3",
                           "%1", "%2", "%3", "Altura", "Peso",
                           "IV", "IV_Vida", "IV_Atk", "IV_Def", "IV_SpA", "IV_SpD", "IV_Vel",
                           "IV_Mag", "IV_Per", "IV_Ene", "IV_EnR", "IV_CrD", "IV_CrC"]:
                try:
                    valor = float(valor)
                except:
                    pass
            info[campo] = valor
    return info
