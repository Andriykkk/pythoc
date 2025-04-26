use num_bigint::BigInt;
use num_traits::cast::ToPrimitive;

fn main() {
    let x = BigInt::from(1);
    let y = (BigInt::from(2) + x).pow(2);  
    println!("{}", y);
}