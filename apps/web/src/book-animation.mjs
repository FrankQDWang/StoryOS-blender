// One timeline owns the cover, hands and transition completion.
export const OPENING_SECONDS = 3.8;
export const CREATION_SECONDS = 3.1;
export const HAND_CONTACTS = {right:[.67,.116,.64],left:[-.16,.230,.63]};
export const ease = (t, a, b) => {
  const u = Math.max(0, Math.min(1, (t-a)/(b-a)));
  return u*u*(3-2*u);
};
export function openingPose(t) {
  return {
    withdraw: ease(t, 0, .30),
    travel: ease(t, .30, 1.0),
    hands: ease(t, .85, 1.35),
    leftHand: ease(t, 1.60, 1.95),
    cover: 2.92*ease(t, 1.42, 2.72),
    pages: [0,1,2].map(i => ease(t, 2.20+(2-i)*.12, 3.20+(2-i)*.12)),
  };
}
