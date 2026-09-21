// Secrets: memory/secrets/<name>.age, one encrypted file per secret, plus a README that
// records the public key and the custody state of the master key's spare.
//
// The convention is the discipline, not the crypto: the kit does not mandate a tool, it
// mandates that a secret VALUE never appears in the clear -- not in a memory file, not in a
// commit, not in a tool result, not in chat.

import type { IsoDate } from './memory-common';

export interface SecretsReadme {
  /** Encrypt-only public key. Safe to commit; that is the point of it. */
  publicKey: string;
  /** Where the private key lives. A PATH, never the key. */
  masterKeyLocation: string;
  /** Custody of the spare: an unrecoverable master key loses every secret at once. */
  spare: {
    deposited: IsoDate | null;
    /** Where, in words. Never a credential. */
    location: string;
    /** Verified how -- e.g. re-deriving the public key from the deposited copy.
     *  Depositing without verifying is depositing nothing. */
    verified: IsoDate | null;
  };
}

// Decrypt into a file or directly into the consumer, never to stdout in a tool result:
// a tool result is transcript, and a transcript is not a vault.
