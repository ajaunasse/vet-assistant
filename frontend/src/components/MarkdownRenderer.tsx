import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '../styles/MarkdownRenderer.css';

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Personnalisation des composants markdown
        p: ({ children }) => <p className="markdown-paragraph">{children}</p>,
        strong: ({ children }) => <strong className="markdown-bold">{children}</strong>,
        em: ({ children }) => <em className="markdown-italic">{children}</em>,
        ul: ({ children }) => <ul className="markdown-list">{children}</ul>,
        ol: ({ children }) => <ol className="markdown-list-ordered">{children}</ol>,
        li: ({ children }) => <li className="markdown-list-item">{children}</li>,
        h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
        h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
        h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
        h4: ({ children }) => <h4 className="markdown-h4">{children}</h4>,
        code: ({ children }) => <code className="markdown-code">{children}</code>,
        pre: ({ children }) => <pre className="markdown-pre">{children}</pre>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;
