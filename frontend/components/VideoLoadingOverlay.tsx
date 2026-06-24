"use client";
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LoadingComposition } from './LoadingComposition';

interface Props {
  stage: string;
  visible: boolean;
}

export default function VideoLoadingOverlay({ stage, visible }: Props) {
  const [Player, setPlayer] = useState<React.ComponentType<any> | null>(null);

  useEffect(() => {
    import('@remotion/player').then(({ Player: P }) => setPlayer(() => P));
  }, []);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            background: 'rgba(8, 8, 14, 0.88)',
            backdropFilter: 'blur(18px)',
            WebkitBackdropFilter: 'blur(18px)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {Player && (
            <motion.div
              initial={{ scale: 0.93, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              style={{
                width: '100%',
                maxWidth: 560,
                borderRadius: 20,
                overflow: 'hidden',
                boxShadow:
                  '0 0 0 1px rgba(34,211,238,0.12), 0 0 60px rgba(34,211,238,0.12), 0 32px 64px rgba(0,0,0,0.6)',
              }}
            >
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
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
