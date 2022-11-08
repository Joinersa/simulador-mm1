import random   # IMPORTAÇÃO DA BIBLIOTECA DE NÚMEROS ALEATÓRIOS.
import simpy    # IMPORTAÇÃO DA BIBLIOTECA DE SIMULAÇÃO.

TEMPO_MEDIO_CHEGADAS = 2.0      # X min para chegar 1 cliente
TEMPO_MEDIO_ATENDIMENTO = 1.0   # Y min para atender 1 cliente

# VARIÁVEIS GLOBAIS
tempo_ocioso_total = 0.0
tempo_de_servico_total = 0.0
instante_do_termino_de_atendimento = 0.0
servidorRes = 0
flag = True


# FUNÇÃO QUE CRIA AS CHEGADAS DOS CLIENTES NO SISTEMA.
def geraChegadas(env):
    contaChegada = 0
    while True:
        # AGUARDA UM INTERVALO DE TEMPO EXPONENCIALMENTE DISTRIBUIDO.
        yield env.timeout(random.expovariate(1.0/TEMPO_MEDIO_CHEGADAS))
        contaChegada += 1
        print('%.1f; Chegada do cliente %d' % (env.now, contaChegada))

        # NOVO EVENTO - O CLIENTE DESISTE DO ATENDIMENTO CASO A FILA ESTEJA COM 5 CLIENTES.
        if len(servidorRes.queue) >= 5:
            print('%.1f; Cliente %d DESISTE DO ATENDIMENTO' % (env.now, contaChegada))
        else:
            # INICIA O PROCESSO DE ATENDIMENTO.
            env.process(atendimentoServidor(env, "cliente %d" % contaChegada, servidorRes))


# FUNÇÃO QUE OCUPA O SERVIDOR E REALIZA O ATENDIMENTO.
def atendimentoServidor(env, nome, servidorRes):

    # INFORMANDO QUE AS VARIÁVEIS USADAS SÃO GLOBAIS.
    global instante_do_termino_de_atendimento
    global tempo_ocioso_total
    global tempo_de_servico_total
    global ir_banheiro
    global flag

    # ARMAZENA O INSTANTE DE CHEGADA DO CLIENTE.
    chegada = env.now

    # SOLICITA O RECURSO "servidorRes"
    request = servidorRes.request()

    # AGUARDA EM FILA ATÉ A LIBERAÇÃO DO RECURSO, DEPOIS O OCUPA.
    yield request

    # CALCULA O TEMPO EM FILA.
    tempo_fila = env.now - chegada

    # CALCULA O TEMPO OCIOSO ANTERIOR (INSTANTE ATUAL menos o INSTANTE DO TERMINO DE ATENDIMENTO ANTERIOR)
    tempo_ocioso_anterior = env.now - instante_do_termino_de_atendimento

    print('%.1f; Servidor inicia o atendimento do %s (tempo em fila: %.1f)' % (env.now, nome, tempo_fila))

    # GUARDA O INSTANTE INICIAL DE ATENDIMENTO
    instante_inicial_de_atendimento = env.now

    # EVENTO DE ATRASO - SERVIDOR IR AO BANHEIRO ----------------
    if env.now >= 5 and flag:
        flag = False
        ir_banheiro = env.event()
        env.process(atrasarAtendimento(env))
        yield env.timeout(2)
        yield ir_banheiro.succeed()

    # AGUARDA O TEMPO DE ATENDIMENTO EXPONENCIALMENTE DISTRIBUIDO
    yield env.timeout(random.expovariate(1.0/TEMPO_MEDIO_ATENDIMENTO))

    print('%.1f; Servidor termina o atendimento do %s; Clientes em fila: %i; Tempo ocioso anterior do servidor: %.1f'
          % (env.now, nome, len(servidorRes.queue), tempo_ocioso_anterior))

    # SOMATÓRIO DO TEMPO OCIOSO TOTAL DO SERVIDOR.
    tempo_ocioso_total += tempo_ocioso_anterior
    # GUARDA O INSTANTE FINAL DE ATENDIMENTO, PARA USAR NA PRÓXIMA ITERAÇÃO.
    instante_do_termino_de_atendimento = env.now

    # SOMATÓRIO DO TEMPO EM SERVIÇO TOTAL DO SERVIDOR.
    tempo_de_servico_total += (instante_do_termino_de_atendimento - instante_inicial_de_atendimento)

    # LIBERA O RECURSO "servidorRes"
    yield servidorRes.release(request)


# FUNÇÃO QUE ATRASA O ATENDIMENTO DO SERVIDOR PARA IR AO BANHEIRO.
def atrasarAtendimento(env):
    global ir_banheiro
    print('%.1f; SERVIDOR FOI AO BANHEIRO' % (env.now))
    yield ir_banheiro # AGUARDA O EVENTO DE IR AO BANHEIRO.
    print('%.1f; SERVIDOR VOLTOU AO ATENDIMENTO' % (env.now))


# FUNÇÃO PRINCIPAL.
def main():
    global servidorRes

    random.seed(25)                                 # SEMENTE GERADORA DE NÚMEROS ALEATÓRIOS.
    env = simpy.Environment()                       # CRIA O 'ENVIRONMENT' DO MODELO.
    servidorRes = simpy.Resource(env, capacity=1)   # CRIA O RECURSO "servidorRes"
    env.process(geraChegadas(env))                  # INICIA O PROCESSO DE GERAÇÃO DE CHEGADAS.
    env.run(until=15)                               # EXECUTA O MODELO POR 15 UNIDADES DE TEMPO (VAMOS SUPOR QUE SEJA MINUTOS)

    print('\nTempo total de atendimento do servidor: %.1f' % tempo_de_servico_total)
    print('Tempo total de ociosidade do servidor: %.1f' % tempo_ocioso_total)

# EXECUTANDO A MAIN.
if __name__ == '__main__':
   main()
