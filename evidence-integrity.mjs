import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';

const sha256=data=>createHash('sha256').update(data).digest('hex');

// Git may normalize CRLF to LF. Normalize line endings only: all other bytes
// (including spaces, JSON values, ordering and source references) remain checked.
export function verifyEvidenceHash(raw,metadata){
 const original=sha256(raw);
 const lf=sha256(raw.toString('utf8').replace(/\r\n/g,'\n'));
 assert.equal(metadata.package_hash_normalization,'utf8-lf-v1','Unknown evidence hash normalization');
 assert.equal(lf,metadata.package_lf_sha256,'Evidence content changed beyond CRLF/LF normalization');
 return {originalHash:original,lfHash:lf,originalBytesMatch:original===metadata.package_sha256};
}
