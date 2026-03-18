def gerar_relatorio(personagem, duracao_minutos, drops, gastos, inimigos, calculos, inimigos_calc, bonus_ativos=None, notas=None):
    horas = duracao_minutos // 60
    minutos = duracao_minutos % 60

    def formatar_inimigo(nome):
        if " - " in nome:
            return nome.split(" - ", 1)[1]
        return nome

    linhas = [
        f"HEADER|{personagem}|{horas}h{minutos:02d}min",
        f"⚔️ Inimigos: {inimigos_calc['total']} ({inimigos_calc['por_hora']}/h)",
    ]

    if inimigos:
        for i in inimigos:
            linhas.append(f"  • {formatar_inimigo(i['inimigo_nome'])} x{i['quantidade']}")

    if bonus_ativos:
        loot = [b for b in bonus_ativos if b["tipo"] == "loot"]
        geral = [b for b in bonus_ativos if b["tipo"] == "geral"]

        if loot:
            linhas.append("SEP")
            linhas.append("🍀 Bônus de Loot:")
            for b in loot:
                h = (b["duracao_minutos"] * b["quantidade"]) // 60
                m = (b["duracao_minutos"] * b["quantidade"]) % 60
                dur = f"{h}h{m:02d}min" if h > 0 else f"{m}min"
                linhas.append(f"  • {b['nome']} x{b['quantidade']} ({dur})")

        if geral:
            linhas.append("⚡ Bônus Gerais:")
            for b in geral:
                h = (b["duracao_minutos"] * b["quantidade"]) // 60
                m = (b["duracao_minutos"] * b["quantidade"]) % 60
                dur = f"{h}h{m:02d}min" if h > 0 else f"{m}min"
                linhas.append(f"  • {b['nome']} x{b['quantidade']} ({dur})")

    linhas.append("SEP")
    linhas.append("📦 Drops:")
    for drop in drops:
        total = drop["quantidade"] * drop["preco_jogador"]
        linhas.append(f"  • {drop['item_nome']} x{drop['quantidade']} — +${total:,}")

    linhas.append("SEP")
    linhas.append("🧪 Gastos:")
    for gasto in gastos:
        preco = gasto.get("preco_pago", 0) if gasto.get("preco_pago", 0) > 0 else gasto["preco_npc"]
        if preco > 0:
            total = gasto["quantidade"] * preco
            linhas.append(f"  • {gasto['item_nome']} x{gasto['quantidade']} — -${total:,}")
        else:
            linhas.append(f"  • {gasto['item_nome']} x{gasto['quantidade']}")

    lucro_jogador = calculos["lucro_jogador"]
    lucro_npc = calculos["lucro_npc"]
    simbolo_jogador = "✅" if lucro_jogador >= 0 else "❌"
    simbolo_npc = "✅" if lucro_npc >= 0 else "❌"

    linhas.append("SEP")
    linhas.append(f"💰 Loot NPC:       +${calculos['total_npc']:,}")
    linhas.append(f"💰 Loot Jogador:   +${calculos['total_jogador']:,}")
    linhas.append(f"💸 Total Gastos:   -${calculos['total_gastos']:,}")
    linhas.append(f"{simbolo_npc} Lucro NPC:      ${lucro_npc:,} (${calculos['lucro_npc_hora']:,}/h)")
    linhas.append(f"{simbolo_jogador} Lucro Jogador:  ${lucro_jogador:,} (${calculos['lucro_jogador_hora']:,}/h)")

    if notas and notas.strip():
        linhas.append("SEP")
        linhas.append("📝 Notas:")
        linhas.append(notas.strip())

    return "\n".join(linhas)