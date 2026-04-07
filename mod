# ==============================
# THE BATTLE CAT (Fan-made Demo)
# ==============================

import random
import time

class Cat:
    def __init__(self, name, hp, atk):
        self.name = name
        self.hp = hp
        self.atk = atk

    def attack(self, enemy):
        damage = random.randint(self.atk - 2, self.atk + 2)
        enemy.hp -= damage
        print(f"{self.name} tấn công {enemy.name} gây {damage} sát thương!")

class Enemy:
    def __init__(self, name, hp, atk):
        self.name = name
        self.hp = hp
        self.atk = atk

    def attack(self, cat):
        damage = random.randint(self.atk - 1, self.atk + 3)
        cat.hp -= damage
        print(f"{self.name} phản công {cat.name} gây {damage} sát thương!")

def battle(cat, enemy):
    print("\n⚔️  BẮT ĐẦU TRẬN CHIẾN - THE BATTLE CAT ⚔️\n")
    time.sleep(1)

    while cat.hp > 0 and enemy.hp > 0:
        cat.attack(enemy)
        if enemy.hp <= 0:
            print(f"\n🐱 {cat.name} CHIẾN THẮNG!")
            break

        enemy.attack(cat)
        if cat.hp <= 0:
            print(f"\n💀 {cat.name} THẤT BẠI...")
            break

        print(f"❤️ {cat.name}: {cat.hp} HP | 👿 {enemy.name}: {enemy.hp} HP\n")
        time.sleep(1)

# Khởi tạo nhân vật
battle_cat = Cat("Battle Cat", hp=50, atk=10)
enemy_dog = Enemy("Evil Doge", hp=40, atk=8)

battle(battle_cat, enemy_dog)
