import {CalculateToolCard} from './CalculateToolCard';
import {WeatherToolCard} from './WeatherToolCard';
import {SearchToolCard} from './SearchToolCard';
import {GenericToolCard} from './GenericToolCard';

export function ToolCallCard({toolCall}) {
    if (toolCall.name === 'calculate') return <CalculateToolCard toolCall={toolCall}/>;
    if (toolCall.name === 'get_weather') return <WeatherToolCard toolCall={toolCall}/>;
    if (toolCall.name === 'search_web') return <SearchToolCard toolCall={toolCall}/>;
    return <GenericToolCard toolCall={toolCall}/>;
}
