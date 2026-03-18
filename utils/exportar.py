def gerar_relatorio(personagem, duracao_minutos, drops, gastos, inimigos, calculos, inimigos_calc, bonus_ativos=None):
    horas = duracao_minutos // 60
    minutos = duracao_minutos % 60

    linhas = [
        f"⚔️ Hunt Report — Personagem: {personagem}",
        f"⏱️ Duração: {horas}h{minutos:02d}min",
        "",
        f"⚔️ Inimigos: {inimigos_calc['total']} ({inimigos_calc['por_hora']}/h)",
        "",
    ]

    if bonus_ativos:
        loot = [b for b in bonus_ativos if b["tipo"] == "loot"]
        geral = [b for b in bonus_ativos if b["tipo"] == "geral"]

        if loot:
            linhas.append("🍀 Bônus de Loot:")
            for b in loot:
                h = (b["duracao_minutos"] * b["quantidade"]) // 60
                m = (b["duracao_minutos"] * b["quantidade"]) % 60
                dur = f"{h}h{m:02d}min" if h > 0 else f"{m}min"
                linhas.append(f"  • {b['nome']} x{b['quantidade']} ({dur} total)")

        if geral:
            linhas.append("⚡ Bônus Gerais:")
            for b in geral:
                h = (b["duracao_minutos"] * b["quantidade"]) // 60
                m = (b["duracao_minutos"] * b["quantidade"]) % 60
                dur = f"{h}h{m:02d}min" if h > 0 else f"{m}min"
                linhas.append(f"  • {b['nome']} x{b['quantidade']} ({dur} total)")

        linhas.append("")

    linhas.append("📦 Drops:")
    for drop in drops:
        linhas.append(f"  • {drop['item_nome']} x{drop['quantidade']}")

    linhas.append("")
    linhas.append("🧪 Gastos:")

    for gasto in gastos:
        linhas.append(f"  • {gasto['item_nome']} x{gasto['quantidade']}")

    linhas += [
        "",
        f"💰 Loot NPC:       {calculos['total_npc']:,} gp",
        f"💰 Loot Jogador:   {calculos['total_jogador']:,} gp",
        f"💸 Total Gastos:   {calculos['total_gastos']:,} gp",
        f"✅ Lucro NPC:      {calculos['lucro_npc']:,} gp ({calculos['lucro_npc_hora']:,}/h)",
        f"✅ Lucro Jogador:  {calculos['lucro_jogador']:,} gp ({calculos['lucro_jogador_hora']:,}/h)",
    ]

    return "\n".join(linhas)