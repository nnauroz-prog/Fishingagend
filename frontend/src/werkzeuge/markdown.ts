import { marked } from 'marked';

marked.setOptions({
  gfm: true,
  breaks: true,
});

export function rendereMarkdown(text: string): string {
  return marked.parse(text) as string;
}
