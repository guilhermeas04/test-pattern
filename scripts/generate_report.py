from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle

OUT = Path('output/pdf/relatorio-test-pattern.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)
S = getSampleStyleSheet()
S.add(ParagraphStyle(name='Cover', parent=S['Title'], alignment=TA_CENTER, fontSize=23, leading=29, textColor=colors.HexColor('#17324D'), spaceAfter=16))
S.add(ParagraphStyle(name='Info', parent=S['Normal'], alignment=TA_CENTER, fontSize=12, leading=20, textColor=colors.HexColor('#384B5F')))
S.add(ParagraphStyle(name='H', parent=S['Heading1'], fontSize=17, leading=21, textColor=colors.HexColor('#17324D'), spaceBefore=5, spaceAfter=9))
S.add(ParagraphStyle(name='H2', parent=S['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#247BA0'), spaceBefore=7, spaceAfter=4))
S.add(ParagraphStyle(name='Body2', parent=S['BodyText'], fontSize=10.2, leading=14.5, textColor=colors.HexColor('#243447'), spaceAfter=7))
S.add(ParagraphStyle(name='Code2', parent=S['Code'], fontName='Courier', fontSize=7.5, leading=9.5, backColor=colors.HexColor('#F1F5F8'), borderPadding=7, spaceBefore=3, spaceAfter=7))

def P(text, style='Body2'):
    return Paragraph(text, S[style])

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#D8E1E8'))
    canvas.line(1.7*cm, 1.35*cm, 19.3*cm, 1.35*cm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#708090'))
    canvas.drawString(1.7*cm, .9*cm, 'Relatorio - Test Patterns')
    canvas.drawRightString(19.3*cm, .9*cm, 'Pagina %d' % doc.page)
    canvas.restoreState()

rows = [['Dependencia', 'Tipo', 'Objetivo'], ['GatewayPagamento', 'Stub', 'Retornar success true e permitir o fluxo.'], ['PedidoRepository', 'Stub', 'Retornar um pedido salvo.'], ['EmailService', 'Mock', 'Verificar chamadas e argumentos.']]
tbl = Table(rows, colWidths=[4.0*cm, 3.0*cm, 10.2*cm])
tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#17324D')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.5), ('GRID', (0,0), (-1,-1), .4, colors.HexColor('#C9D5DF')), ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F5F8FA')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 6)]))

story = [
    Spacer(1, 2.0*cm), P('RELATORIO DE TEST PATTERNS', 'Cover'), P('Object Mother, Data Builder e Test Doubles', 'Info'), Spacer(1, 2.0*cm),
    P('<b>Disciplina:</b> Testes de Software', 'Info'), P('<b>Trabalho:</b> Implementacao de Padroes de Teste', 'Info'), P('<b>Nome:</b> A preencher', 'Info'), P('<b>Matricula:</b> A preencher', 'Info'), Spacer(1, 2.5*cm), P('Projeto: test-pattern', 'Info'), P('Novembro de 2026', 'Info'), PageBreak(),
    P('1. Padroes de criacao de dados', 'H'), P('Os testes do CheckoutService utilizam dois padroes complementares. O UserMother concentra usuarios estaveis e recorrentes, enquanto o CarrinhoBuilder permite montar cenarios variados sem esconder os detalhes relevantes.'), P('1.1 Por que CarrinhoBuilder em vez de CarrinhoMother?', 'H2'), P('O carrinho e um objeto composto por usuario e uma colecao de itens. Como cada cenario pode alterar quantidade, preco, usuario ou estado vazio, um CarrinhoMother exigiria muitos metodos combinatorios. Essa API cresceria rapidamente e seria dificil de manter.'), P('O CarrinhoBuilder comeca com valores padrao e permite sobrescrever somente o que importa. Os metodos comUser, comItens e vazio deixam a intencao visivel, enquanto build cria a instancia final.'), P('1.2 Exemplo: setup manual versus Data Builder', 'H2'), P('<b>Antes - setup manual:</b>'), Preformatted("const user = new User(2, 'Usuario Premium',\n  'premium@email.com', 'PREMIUM');\nconst item = new Item('Produto premium', 200);\nconst carrinho = new Carrinho(user, [item]);", S['Code2']), P('<b>Depois - setup com Builder:</b>'), Preformatted("const carrinho = new CarrinhoBuilder()\n  .comUser(UserMother.umUsuarioPremium())\n  .comItens([new Item('Produto premium', 200)])\n  .build();", S['Code2']), P('No segundo exemplo, a leitura se aproxima da regra de negocio: um cliente Premium finaliza uma compra de R$ 200. O teste declara apenas as variacoes importantes.'), P('1.3 Legibilidade e manutencao', 'H2'), P('A API fluente reduz o Setup Obscuro. Se a estrutura de Carrinho ganhar um novo campo obrigatorio, a alteracao pode ficar concentrada no Builder, preservando os testes. Os defaults mantem casos simples curtos.'), PageBreak(),
    P('2. Test Doubles: Mocks versus Stubs', 'H'), P('O teste de sucesso Premium combina doubles com papeis diferentes. GatewayPagamento e PedidoRepository controlam o fluxo por meio de retornos previsiveis. EmailService e observado para verificar uma interacao especifica.'), P('2.1 Cenario Premium', 'H2'), tbl, Spacer(1, 9), P('O GatewayPagamento e principalmente um Stub porque o interesse do teste e controlar o resultado externo. Ao retornar success true, o teste verifica o desconto e permite que o checkout avance. O PedidoRepository tambem e Stub porque fornece um pedido salvo previsivel.'), P('O EmailService e um Mock porque o comportamento observado e a interacao. O teste exige exatamente uma chamada, para o destinatario correto, com assunto e corpo esperados.'), Preformatted("expect(gatewayStub.cobrar).toHaveBeenCalledWith(180, cartaoCredito);\nexpect(emailMock.enviarEmail).toHaveBeenCalledTimes(1);\nexpect(emailMock.enviarEmail).toHaveBeenCalledWith(\n  'premium@email.com', 'Seu Pedido foi Aprovado!',\n  'Pedido 456 no valor de R$180'\n);", S['Code2']), P('O cenario segue Arrange-Act-Assert: prepara o carrinho e os doubles, executa processarPedido e verifica desconto e notificacao.'), PageBreak(),
    P('3. Conclusao', 'H'), P('Builders e Test Doubles tornam explicita a intencao dos testes. O UserMother evita duplicar a criacao de usuarios estaveis; o CarrinhoBuilder representa melhor a variabilidade natural de um carrinho.'), P('A distincao entre Stub e Mock torna a suite mais precisa. Stubs controlam respostas e isolam o fluxo de dependencias externas. Mocks registram interacoes que fazem parte do comportamento esperado, como o envio de um e-mail.'), P('A suite cobre falha de pagamento, checkout padrao, desconto Premium e envio de e-mail. Com quatro testes passando, os padroes ajudam a prevenir Setup Obscuro, duplicacao e acoplamento excessivo, contribuindo para uma suite sustentavel.'), Spacer(1, 12), P('<b>Validacao:</b> npm test - 1 suite aprovada, 4 testes aprovados.')
]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm, topMargin=1.6*cm, bottomMargin=1.7*cm, title='Relatorio de Test Patterns')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
