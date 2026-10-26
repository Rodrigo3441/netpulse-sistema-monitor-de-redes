from src.data_labeling import (
    build_baseline,
    calculate_metrics,
    label_period_b,
    split_dataset
)

def execute():
    print('Construindo o baseline: ')
    build_baseline.main()

    print('Calculando as métricas derivadas: ')
    calculate_metrics.main()

    print('Rotulando o dataset B')
    label_period_b.main()

    print('Separando dados entre treino, validação e teste')
    split_dataset.main()


