use num_bigint::BigInt;
use num_traits::cast::ToPrimitive;
fn main() {
let x: BigInt = BigInt::from(1);
let y: BigInt = BigInt::from(1) << (x).to_u32().unwrap();
println!("{}", y);
}
