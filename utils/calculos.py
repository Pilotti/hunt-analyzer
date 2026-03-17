def calcular_hunt(duracao_minutos, drops, gastos):
    horas = duracao_minutos / 60

    total_npc = sum(d["quantidade"] * d["preco_npc"] for d in drops)
    total_jogador = sum(d["quantidade"] * d["preco_jogador"] for d in drops)
    total_gastos = sum(g["quantidade"] * g["preco_npc"] for g in gastos)

    lucro_npc = total_npc - total_gastos
    lucro_jogador = total_jogador - total_gastos

    return {
        "total_npc": total_npc,
        "total_jogador": total_jogador,
        "total_gastos": total_gastos,
        "lucro_npc": lucro_npc,
        "lucro_jogador": lucro_jogador,
        "lucro_npc_hora": round(lucro_npc / horas) if horas > 0 else 0,
        "lucro_jogador_hora": round(lucro_jogador / horas) if horas > 0 else 0,
    }

def calcular_inimigos(quantidade, duracao_minutos):
    horas = duracao_minutos / 60
    return {
        "total": quantidade,
        "por_hora": round(quantidade / horas) if horas > 0 else 0
    }