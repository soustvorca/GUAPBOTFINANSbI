import matplotlib.pyplot as plt
import os

def generate_pie_chart(categories: list, amounts: list, filename: str = "chart.png") -> str:
    """
    Генерирует круговую диаграмму расходов и сохраняет её в файл.
    """
    # Настройка шрифта для корректного отображения кириллицы (русских букв)
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans'] 
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Построение круговой диаграммы с процентами
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, 
           colors=plt.cm.Pastel1.colors)
    ax.set_title('Структура расходов')
    
    # Сохранение изображения с высоким качеством
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig) # Очищаем память
    
    return filename