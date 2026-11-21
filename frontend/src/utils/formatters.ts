/**
 * Formatting utilities conforming to the non-negotiable coding standards:
 * strictly zero floating-point arithmetic on currency, weights, or purities.
 */

export function formatPaiseToINR(paise: number): string {
  const isNegative = paise < 0;
  const absPaise = Math.abs(paise);
  const rupees = Math.floor(absPaise / 100);
  const subPaise = absPaise % 100;

  const rupeeStr = rupees.toString();
  let formattedRupees = rupeeStr;

  if (rupeeStr.length > 3) {
    const lastThree = rupeeStr.substring(rupeeStr.length - 3);
    const rest = rupeeStr.substring(0, rupeeStr.length - 3);
    const groups: string[] = [];
    let cur = rest;
    while (cur.length > 2) {
      groups.unshift(cur.substring(cur.length - 2));
      cur = cur.substring(0, cur.length - 2);
    }
    if (cur.length > 0) {
      groups.unshift(cur);
    }
    formattedRupees = groups.join(',') + ',' + lastThree;
  }

  const sign = isNegative ? '-' : '';
  const subPaiseStr = subPaise.toString().padStart(2, '0');
  return `${sign}₹${formattedRupees}.${subPaiseStr}`;
}

export function formatMgToGrams(mg: number): string {
  const isNegative = mg < 0;
  const absMg = Math.abs(mg);
  const wholeG = Math.floor(absMg / 1000);
  const fracMg = absMg % 1000;
  const sign = isNegative ? '-' : '';
  return `${sign}${wholeG}.${fracMg.toString().padStart(3, '0')} g`;
}

export function formatPermille(permille: number): string {
  const whole = Math.floor(permille / 10);
  const frac = (permille % 10) * 10;
  return `${whole}.${frac.toString().padStart(2, '0')}% (${permille}‰)`;
}

export function truncateHash(hash: string, lead = 8, trail = 8): string {
  if (!hash || hash.length <= lead + trail) return hash;
  return `${hash.slice(0, lead)}...${hash.slice(-trail)}`;
}
