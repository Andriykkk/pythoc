use num_bigint::BigInt;
use num_traits::cast::ToPrimitive;

fn main() {
    let x = BigInt::from(1);
    let y = 1 as f64 + (BigInt::from(2) + x).to_f64().unwrap() + 2.0;  
    // let y = x + BigInt::from(2) + BigInt::from(10);
    println!("{}", y);
}