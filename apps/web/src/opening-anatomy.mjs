// The book varies by lectern, but the person does not. Preserve a finger contact
// anchor while canceling only the book's scale on each complete skinned arm.
import anatomy from './opening-anatomy.json' with {type:'json'};
export const HAND_REFERENCE_BOOK_SCALE=anatomy.referenceBookScale;
export function fitHandsToBook(arms,bookScale){
 const scale=HAND_REFERENCE_BOOK_SCALE/bookScale;
 for(const {arm,contact,point} of arms){
  arm.position.set(0,0,0);arm.scale.setScalar(1);
  arm.updateWorldMatrix(true,true);
  contact.getWorldPosition(point);arm.worldToLocal(point);
  arm.scale.setScalar(scale);
  arm.position.copy(point).multiplyScalar(1-scale);
  arm.updateWorldMatrix(false,true);
 }
}
