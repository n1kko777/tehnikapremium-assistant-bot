/**
 * Скрипт для встраивания виджета ТехникаПремиум на сайт
 * 
 * Использование:
 * <script src="https://your-server.com/static/embed.js" data-api-url="https://your-server.com"></script>
 */

(function() {
    'use strict';

    // Получаем URL API из атрибута скрипта
    const script = document.currentScript;
    const apiUrl = script.getAttribute('data-api-url') || '';
    const position = script.getAttribute('data-position') || 'right';
    const primaryColor = script.getAttribute('data-color') || '#00d9ff';
    
    // Загружаем основной виджет
    const widgetScript = document.createElement('script');
    widgetScript.src = apiUrl + '/static/widget.js';
    widgetScript.onload = function() {
        // Инициализируем виджет после загрузки
        if (window.TehnikaPremiumWidget) {
            window.TehnikaPremiumWidget.init({
                apiUrl: apiUrl,
                position: position,
                primaryColor: primaryColor,
                title: 'Консультант ТехникаПремиум',
                placeholder: 'Напишите ваш вопрос...',
                welcomeMessage: 'Здравствуйте! 👋 Я AI-консультант ТехникаПремиум. Помогу подобрать бытовую технику, расскажу о характеристиках и ценах. Чем могу помочь?'
            });
        }
    };
    
    document.head.appendChild(widgetScript);
})();

