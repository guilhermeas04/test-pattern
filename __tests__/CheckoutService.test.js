import { CheckoutService } from '../src/services/CheckoutService.js';
import { Item } from '../src/domain/Item.js';
import { UserMother } from './builders/UserMother.js';
import { CarrinhoBuilder } from './builders/CarrinhoBuilder.js';

describe('CheckoutService', () => {
    const cartaoCredito = { numero: '4111111111111111' };

    function criarDependencias({ pagamento = { success: true } } = {}) {
        const gateway = { cobrar: jest.fn().mockResolvedValue(pagamento) };
        const repository = {
            salvar: jest.fn().mockImplementation(async (pedido) => ({
                ...pedido,
                id: 123
            }))
        };
        const emailService = { enviarEmail: jest.fn().mockResolvedValue() };

        return { gateway, repository, emailService };
    }

    describe('quando o pagamento falha', () => {
        it('retorna null sem chamar as outras dependências', async () => {
            const carrinho = new CarrinhoBuilder()
                .comUser(UserMother.umUsuarioPadrao())
                .build();
            const gatewayStub = {
                cobrar: jest.fn().mockResolvedValue({ success: false })
            };
            const repositoryDummy = {};
            const emailServiceDummy = {};
            const checkoutService = new CheckoutService(
                gatewayStub,
                repositoryDummy,
                emailServiceDummy
            );

            const pedido = await checkoutService.processarPedido(
                carrinho,
                cartaoCredito
            );

            expect(pedido).toBeNull();
            expect(gatewayStub.cobrar).toHaveBeenCalledWith(100, cartaoCredito);
        });
    });

    it('retorna o pedido salvo com o total integral para um usuário padrão', async () => {
        const dependencies = criarDependencias();
        const service = new CheckoutService(
            dependencies.gateway,
            dependencies.repository,
            dependencies.emailService
        );

        const result = await service.processarPedido(
            new CarrinhoBuilder()
                .comUser(UserMother.umUsuarioPadrao())
                .build(),
            cartaoCredito
        );

        expect(result.id).toBe(123);
        expect(result.totalFinal).toBe(100);
        expect(dependencies.gateway.cobrar).toHaveBeenCalledWith(100, cartaoCredito);
    });

    describe('quando um cliente Premium finaliza a compra', () => {
        it('aplica o desconto e envia o e-mail de aprovação', async () => {
            const usuarioPremium = UserMother.umUsuarioPremium();
            const carrinho = new CarrinhoBuilder()
                .comUser(usuarioPremium)
                .comItens([new Item('Produto premium', 200)])
                .build();
            const gatewayStub = {
                cobrar: jest.fn().mockResolvedValue({ success: true })
            };
            const repositoryStub = {
                salvar: jest.fn().mockResolvedValue({
                    id: 456,
                    carrinho,
                    totalFinal: 180,
                    status: 'PROCESSADO'
                })
            };
            const emailMock = {
                enviarEmail: jest.fn().mockResolvedValue()
            };
            const checkoutService = new CheckoutService(
                gatewayStub,
                repositoryStub,
                emailMock
            );

            await checkoutService.processarPedido(carrinho, cartaoCredito);

            expect(gatewayStub.cobrar).toHaveBeenCalledWith(180, cartaoCredito);
            expect(emailMock.enviarEmail).toHaveBeenCalledTimes(1);
            expect(emailMock.enviarEmail).toHaveBeenCalledWith(
                'premium@email.com',
                'Seu Pedido foi Aprovado!',
                'Pedido 456 no valor de R$180'
            );
        });
    });

    it('envia e-mail com os dados do pedido após o pagamento', async () => {
        const dependencies = criarDependencias();
        const service = new CheckoutService(
            dependencies.gateway,
            dependencies.repository,
            dependencies.emailService
        );

        await service.processarPedido(
            new CarrinhoBuilder()
                .comUser(UserMother.umUsuarioPadrao())
                .build(),
            cartaoCredito
        );

        expect(dependencies.emailService.enviarEmail).toHaveBeenCalledWith(
            'padrao@example.com',
            'Seu Pedido foi Aprovado!',
            'Pedido 123 no valor de R$100'
        );
    });
});
