

export function Disclosure({ question, answer }: { question: string; answer: string }) {
  return (
    <details>
      <summary>{question}</summary>
      <p>{answer}</p>
    </details>
  );
}