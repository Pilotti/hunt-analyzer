def gerar_relatorio(personagem, duracao_minutos, drops, gastos, inimigos, calculos, inimigos_calc):
    horas = duracao_minutos // 60
    minutos = duracao_minutos % 60

    linhas = [
        f"🗡️ Hunt Report — Personagem: {personagem}",
        f"⏱️ Duração: {horas}h{minutos:02d}min",
        "",
        f"⚔️ Inimigos: {inimigos_calc['total']} ({inimigos_calc['por_hora']}/h)",
        "",
        "📦 Drops:",
    ]

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