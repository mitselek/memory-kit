// Keys: memory/keys.yaml. One row per access grant the home holds or has handed out.
//
// The tier exists for the REVOKE column. Grants accumulate silently -- a token here, a share
// there, a collaborator added once -- and the moment nobody can say how a grant is withdrawn,
// it is permanent by accident.

import type { IsoDate, Ref } from './memory-common';

export interface KeysFile {
  keys: KeyGrant[];
}

export interface KeyGrant {
  /** What the grant is over: a service, a repo, a device, a share. */
  subject: string;
  /** Who holds it. A role or an account, never a credential value. */
  holder: string;
  /** What it permits, in a few words. */
  scope: string;
  granted: IsoDate;
  /** THE POINT OF THIS TIER: the exact step that withdraws it.
   *  A command, a page, a person to ask. Blank is a finding, not a blank. */
  revoke: string;
  ref: Ref;
}

// Reviewed when the sweep runs. A grant whose `revoke` is blank is the tier's own alarm.
