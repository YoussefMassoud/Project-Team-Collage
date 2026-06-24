"use client";
import { useEffect, useState } from 'react';
import { LoadingComposition } from './LoadingComposition';

interface Props {
  stage: string;
}

export default function VideoLoadingPlayer({ stage }: Props) {
  const [Player, setPlayer] = useState<React.ComponentType<any> | null>(null);

  useEffect(() => {
    import('@remotion/player').then(({ Player: P }) => setPlayer(() => P));
  }, []);

  if (!Player) return null;

  return (
    <Player
      component={LoadingComposition}
      durationInFrames={90}
      fps={30}
      compositionWidth={640}
      compositionHeight={360}
      style={{ width: '100%', display: 'block' }}
      loop
      autoPlay
      controls={false}
      inputProps={{ stage }}
    />
  );
}
