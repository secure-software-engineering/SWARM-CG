function func() {
  return true;
}

const a = Array.from({ length: 10 }, (_, i) => i).filter(_ => func());