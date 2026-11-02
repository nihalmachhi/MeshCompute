export const faq = [
  { q: "Is it safe to run?", a: "Yes in a lab. Decoys are inert and network-isolated." },
  { q: "Why can't decoys reach the internet?", a: "They sit on an internal-only network." },
  { q: "What is stored about a login attempt?", a: "A user class and password length plus a keyed hash." },
  { q: "What does tamper-evident mean here?", a: "An HMAC hash chain with checkpoints." },
  { q: "Are the ATT&CK labels certain?", a: "They are rule-based with evidence, not certainty." },
  { q: "What does the bandit do?", a: "It proposes decoy changes for analyst approval." },
  { q: "Can I put it on a public IP?", a: "No, lab only." },
  { q: "What is the panic switch?", a: "It stops all decoys immediately." },
  { q: "Is it production ready?", a: "No." },
];